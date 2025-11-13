import math
import pygame
import pygame_gui
import networkx as nx
from src.enums.colors import Colors

from typing import TYPE_CHECKING, Tuple, Optional, Set

if TYPE_CHECKING:
    from src.states.gameplay import GameplayState


class GraphVisualization:
    """Interactive graph visualization using NetworkX and pygame"""

    def __init__(self, state: "GameplayState", rect: pygame.Rect):
        self.state = state
        self.rect = rect  # Area where graph is rendered
        self.graph = nx.DiGraph()
        self.pos = {}  # Node positions (computed once, kept static)
        self.node_attributes = {}  # Store node attributes (name, role, etc.)
        self.edge_attributes = {}  # Store edge attributes
        self.layout_computed = False
        self.current_level = None

        # Interaction state
        self.selected_node = None
        self.selected_edge = None  # Tuple of (source, target) or None
        self.highlighted_nodes: Set[str] = set()
        self.dragging_node = None
        self.drag_offset = (0, 0)
        self.zoom = 1.0
        self.pan_offset = (0, 0)
        self.panning = False
        self.pan_start = (0, 0)

        # Track click state for showing details only on click-and-release
        self.click_start_pos = None
        self.click_start_node = None
        self.click_start_edge = None
        self.has_dragged = False

        # Details overlay (for both nodes and edges)
        self.show_node_details = False
        self.show_edge_details = False
        self.details_node_id = None
        self.details_edge = None  # Tuple of (source, target) or None
        self.details_panel = None

        # Visual settings
        self.node_radius = 15
        self.node_colors = {
            "Suspect": Colors.ACCENT.value,
            "Victim": (200, 80, 80),  # Red-ish
            "Location": (100, 150, 200),  # Blue-ish
            "Bank": (100, 200, 150),  # Green-ish
        }
        self.default_node_color = (128, 128, 128)  # Gray
        self.edge_color = (100, 100, 120)
        self.selected_color = Colors.SUCCESS.value
        self.highlight_color = Colors.ACCENT.value

    def clean_up(self):
        """Clean up the graph visualization"""
        self.state = None

    def load_graph_for_level(self, level_num: int):
        """Load graph from Neo4j filtered by graph_n property for current level"""
        if self.current_level == level_num and self.layout_computed:
            return  # Already loaded for this level

        self.current_level = level_num
        self.graph.clear()
        self.node_attributes.clear()
        self.edge_attributes.clear()
        self.layout_computed = False
        self.selected_node = None
        self.selected_edge = None
        self.highlighted_nodes.clear()

        try:
            # Query all nodes
            nodes_query = """
            MATCH (n)
            RETURN labels(n) as labels, properties(n) as props, elementId(n) as id
            """
            # Query all relationships
            relationships_query = """
            MATCH (a)-[r]->(b)
            RETURN elementId(a) as source, type(r) as relationship, 
                   elementId(b) as target, properties(r) as props
            """
            nodes_data = self.state.game.db.execute_query(nodes_query)
            relationships_data = self.state.game.db.execute_query(relationships_query)

            # Filter nodes by level
            graph_prop = f"graph_{level_num - 1}" if level_num > 0 else "graph_0"
            filtered_nodes = []
            for node in nodes_data:
                props = node["props"]
                labels = node["labels"]
                if ("Suspect" not in labels and "Bank" not in labels) or props.get(
                    graph_prop, False
                ):
                    filtered_nodes.append(node)

            # Filter relationships by nodes
            filtered_node_ids = {node["id"] for node in filtered_nodes}
            filtered_relationships = []
            for rel in relationships_data:
                if (
                    rel["source"] in filtered_node_ids
                    and rel["target"] in filtered_node_ids
                ):
                    filtered_relationships.append(rel)

            # Add nodes to NetworkX graph
            for node in filtered_nodes:
                node_id = node["id"]
                labels = node["labels"]
                props = node["props"]
                primary_label = labels[0] if labels else "Unknown"
                node_name = props.get("name", primary_label)

                # Store attributes
                self.node_attributes[node_id] = {
                    "labels": labels,
                    "primary_label": primary_label,
                    "name": node_name,
                    "properties": props,
                }
                self.graph.add_node(node_id)

            # Add edges
            for rel in filtered_relationships:
                source = rel["source"]
                target = rel["target"]
                rel_type = rel["relationship"]
                rel_props = rel.get("props", {})

                if source in self.graph and target in self.graph:
                    edge_key = (source, target)
                    self.edge_attributes[edge_key] = {
                        "type": rel_type,
                        "properties": rel_props,
                    }
                    self.graph.add_edge(source, target)

            # Compute layout once
            self._compute_layout()
            self.layout_computed = True

        except Exception as e:
            print(f"Error loading graph for level {level_num}: {e}")

    def _compute_layout(self):
        """Compute node positions using NetworkX layout algorithm"""
        if len(self.graph) == 0:
            return

        # Use spring layout for better visualization
        # Scale to fit within the rect
        pos = nx.spring_layout(
            self.graph,
            k=2.0,
            iterations=50,
            seed=73,
        )

        # Scale and translate to fit in rect
        if pos:
            # Get bounding box of positions
            x_coords = [p[0] for p in pos.values()]
            y_coords = [p[1] for p in pos.values()]

            if x_coords and y_coords:
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)

                # Add padding
                padding = 50
                width = max_x - min_x if max_x != min_x else 1
                height = max_y - min_y if max_y != min_y else 1

                # Scale to fit rect with padding
                scale_x = (self.rect.width - 2 * padding) / width if width > 0 else 1
                scale_y = (self.rect.height - 2 * padding) / height if height > 0 else 1
                scale = min(scale_x, scale_y)

                # Center in rect
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                rect_center_x = self.rect.centerx
                rect_center_y = self.rect.centery

                # Transform positions
                for node_id, (x, y) in pos.items():
                    # Scale and center
                    new_x = (x - center_x) * scale + rect_center_x
                    new_y = (y - center_y) * scale + rect_center_y
                    self.pos[node_id] = (new_x, new_y)

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events for interaction"""
        consumed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                if self.rect.collidepoint(mouse_pos):
                    # Track click start for detecting drags
                    self.click_start_pos = mouse_pos
                    self.has_dragged = False

                    # Check if clicking on a node first (nodes are larger targets)
                    clicked_node = self._get_node_at_position(mouse_pos)
                    if clicked_node:
                        self.selected_node = clicked_node
                        self.selected_edge = None
                        self.dragging_node = clicked_node
                        self.click_start_node = clicked_node
                        self.click_start_edge = None
                        node_pos = self.pos[clicked_node]
                        self.drag_offset = (  # offset of the node from the mouse position, to prevent snapping to the node
                            mouse_pos[0] - node_pos[0],
                            mouse_pos[1] - node_pos[1],
                        )
                        # Don't show details yet - wait for mouse release
                    else:
                        # Check if clicking on an edge
                        clicked_edge = self._get_edge_at_position(mouse_pos)
                        if clicked_edge:
                            self.selected_edge = clicked_edge
                            self.selected_node = None
                            self.click_start_edge = clicked_edge
                            self.click_start_node = None
                            # Don't show details yet - wait for mouse release
                        else:
                            # Start panning
                            self.panning = True
                            self.pan_start = mouse_pos
                            self.selected_node = None
                            self.selected_edge = None
                            self.click_start_node = None
                            self.click_start_edge = None
                            self.show_node_details = False
                            self.show_edge_details = False
                            if self.details_panel:
                                self.details_panel.kill()
                                self.details_panel = None
                    consumed = True

            elif event.button == 4:  # Scroll up
                if self.rect.collidepoint(event.pos):
                    self.zoom = min(self.zoom * 1.1, 3.0)
                    consumed = True
            elif event.button == 5:  # Scroll down
                if self.rect.collidepoint(event.pos):
                    self.zoom = max(self.zoom / 1.1, 0.5)
                    consumed = True
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos

            # Check if we've moved enough to consider it a drag (for both nodes and edges)
            if self.click_start_pos:
                drag_distance = (
                    (mouse_pos[0] - self.click_start_pos[0]) ** 2
                    + (mouse_pos[1] - self.click_start_pos[1]) ** 2
                ) ** 0.5
                if drag_distance > 5:  # Threshold for considering it a drag
                    self.has_dragged = True

            if self.dragging_node and self.dragging_node in self.pos:
                # Update node position
                self.pos[self.dragging_node] = (
                    mouse_pos[0] - self.drag_offset[0],
                    mouse_pos[1] - self.drag_offset[1],
                )
                consumed = True
            elif self.panning:
                dx = mouse_pos[0] - self.pan_start[0]
                dy = mouse_pos[1] - self.pan_start[1]
                self.pan_offset = (
                    self.pan_offset[0] + dx,
                    self.pan_offset[1] + dy,
                )
                self.pan_start = mouse_pos
                consumed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                # Show details panel only if we didn't drag
                if not self.has_dragged:
                    if self.click_start_node:
                        self._show_node_details(self.click_start_node)
                    elif self.click_start_edge:
                        self._show_edge_details(self.click_start_edge)

                # Clean up click tracking
                self.dragging_node = None
                self.panning = False
                self.click_start_pos = None
                self.click_start_node = None
                self.click_start_edge = None
                self.has_dragged = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.selected_node = None
                self.selected_edge = None
                self.show_node_details = False
                self.show_edge_details = False
                if self.details_panel:
                    self.details_panel.kill()
                    self.details_panel = None
                    consumed = True
            elif event.mod & pygame.KMOD_CTRL:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.zoom = min(self.zoom * 1.3, 3.0)
                        consumed = True
                    elif event.key == pygame.K_MINUS:
                        self.zoom = max(self.zoom / 1.3, 0.5)
                        consumed = True
        return consumed

    def _get_node_at_position(self, pos: Tuple[int, int]) -> Optional[str]:
        """Get node ID at given screen position"""
        for node_id, node_pos in self.pos.items():
            # Apply zoom and pan transforms
            transformed_pos = self._transform_position(node_pos)
            # If Euclidean distance is less than or equal to node radius * zoom, return node ID
            distance = (
                (pos[0] - transformed_pos[0]) ** 2 + (pos[1] - transformed_pos[1]) ** 2
            ) ** 0.5
            if distance <= self.node_radius * self.zoom:
                return node_id
        return None

    def _get_edge_at_position(self, pos: Tuple[int, int]) -> Optional[Tuple[str, str]]:
        """Get edge at given screen position"""
        for source, target in self.graph.edges():
            if source in self.pos and target in self.pos:
                start_pos = self._transform_position(self.pos[source])
                end_pos = self._transform_position(self.pos[target])
                if self._is_point_on_line(pos, (start_pos, end_pos)):
                    return (source, target)
        return None

    def _is_point_on_line(
        self,
        point: Tuple[int, int],
        line: Tuple[Tuple[int, int], Tuple[int, int]],
        thickness: float = 2,
        tolerance: float = 2,
    ) -> bool:
        """Check if point is visually on a finite line segment."""
        (x1, y1), (x2, y2) = line
        x, y = point

        # Compute a margin for visual thickness
        margin = (thickness / 2) + tolerance

        # Quick bounding box rejection
        if (
            x < min(x1, x2) - margin
            or x > max(x1, x2) + margin
            or y < min(y1, y2) - margin
            or y > max(y1, y2) + margin
        ):
            return False

        # Degenerate case: start == end
        line_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if line_len_sq == 0:
            return math.hypot(x - x1, y - y1) <= margin

        # Cross product (for perpendicular distance)
        cross = abs((x - x1) * (y2 - y1) - (y - y1) * (x2 - x1))
        distance = cross / math.sqrt(line_len_sq)

        return distance <= margin

    def _transform_position(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Apply zoom and pan transforms to a position"""
        x, y = pos
        # Apply pan
        x += self.pan_offset[0]
        y += self.pan_offset[1]
        # Apply zoom around rect center
        center_x, center_y = self.rect.center
        x = center_x + (x - center_x) * self.zoom
        y = center_y + (y - center_y) * self.zoom
        return (x, y)

    def _show_node_details(self, node_id: str):
        """Show node details in a UI overlay"""
        self.show_node_details = True
        self.details_node_id = node_id

        # Create details panel if it doesn't exist
        if self.details_panel:
            self.details_panel.kill()

        attrs = self.node_attributes.get(node_id, {})
        props = attrs.get("properties", {})
        name = attrs.get("name", "Unknown")
        labels = attrs.get("labels", [])
        pos = self.pos.get(node_id, (0, 0))

        # Create text content
        lines = [f"Node Name: {name}"]
        lines.append(f"Type: {', '.join(labels)}")
        lines.append("")
        lines.append("Properties:")
        for key, value in props.items():
            if not key.startswith("graph_"):  # Skip graph_n properties
                lines.append(f"  {key}: {value}")

        # Create panel
        panel_width = 300
        instruction_height = 25  # Space for instruction text
        panel_height = min(400, len(lines) * 25 + 40) + instruction_height
        panel_x = int(self._transform_position(pos)[0] - panel_width / 2)
        panel_y = int(self._transform_position(pos)[1] + self.node_radius * self.zoom)

        self.details_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            manager=self.state.pygame_gui_manager,
            object_id="#node_details_panel",
        )

        # Add text (leave room for instruction at bottom)
        details_panel_border_thickness = 1
        text_rect = pygame.Rect(
            10,
            10,
            panel_width - 20 - 2 * details_panel_border_thickness,
            panel_height - 20 - instruction_height - 2 * details_panel_border_thickness,
        )
        text_box = pygame_gui.elements.UITextBox(
            relative_rect=text_rect,
            html_text="<br>".join(lines),
            manager=self.state.pygame_gui_manager,
            container=self.details_panel,
        )

        # Add instruction text at bottom
        instruction_rect = pygame.Rect(
            10,
            panel_height - instruction_height - 5,
            panel_width - 20,
            instruction_height,
        )
        instruction_label = pygame_gui.elements.UILabel(
            relative_rect=instruction_rect,
            text="Press 'TAB' to close",
            manager=self.state.pygame_gui_manager,
            container=self.details_panel,
        )

    def _show_edge_details(self, edge: Tuple[str, str]):
        """Show edge details in a UI overlay"""
        self.show_edge_details = True
        self.details_edge = edge
        source, target = edge

        # Create details panel if it doesn't exist
        if self.details_panel:
            self.details_panel.kill()

        attrs = self.edge_attributes.get(edge, {})
        rel_type = attrs.get("type", "Unknown")
        props = attrs.get("properties", {})

        # Get source and target node names
        source_attrs = self.node_attributes.get(source, {})
        target_attrs = self.node_attributes.get(target, {})
        source_name = source_attrs.get("name", "Unknown")
        target_name = target_attrs.get("name", "Unknown")

        # Calculate position for panel (midpoint of edge)
        source_pos = self._transform_position(self.pos[source])
        target_pos = self._transform_position(self.pos[target])
        edge_midpoint = (
            (source_pos[0] + target_pos[0]) / 2,
            (source_pos[1] + target_pos[1]) / 2,
        )

        # Create text content
        lines = [f"Relationship: {rel_type}"]
        lines.append(f"From: {source_name}")
        lines.append(f"To: {target_name}")
        lines.append("")
        if props:
            lines.append("Properties:")
            for key, value in props.items():
                if not key.startswith("graph_"):  # Skip graph_n properties
                    lines.append(f"  {key}: {value}")
        else:
            lines.append("No properties")

        # TODO: Code below this is duplicated from _show_node_details, should be refactored
        # Create panel
        panel_width = 300
        instruction_height = 25  # Space for instruction text
        panel_height = min(400, len(lines) * 25 + 40) + instruction_height
        panel_x = int(edge_midpoint[0] - panel_width / 2)
        panel_y = int(edge_midpoint[1] + 20)

        self.details_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            manager=self.state.pygame_gui_manager,
            object_id="#edge_details_panel",
        )

        # Add text (leave room for instruction at bottom)
        text_rect = pygame.Rect(
            10, 10, panel_width - 20, panel_height - 20 - instruction_height
        )
        text_box = pygame_gui.elements.UITextBox(
            relative_rect=text_rect,
            html_text="<br>".join(lines),
            manager=self.state.pygame_gui_manager,
            container=self.details_panel,
        )

        # Add instruction text at bottom
        instruction_rect = pygame.Rect(
            10,
            panel_height - instruction_height - 5,
            panel_width - 20,
            instruction_height,
        )
        instruction_label = pygame_gui.elements.UILabel(
            relative_rect=instruction_rect,
            text="Press 'TAB' to close",
            manager=self.state.pygame_gui_manager,
            container=self.details_panel,
        )

    def highlight_nodes(self, node_ids: Set[str]):
        """Highlight specific nodes"""
        self.highlighted_nodes = node_ids

    def render(self, screen: pygame.Surface):
        """Render the graph visualization"""
        if not self.layout_computed or len(self.graph) == 0:
            return

        # Save the current clipping rectangle
        old_clip = screen.get_clip()

        # Set clipping rectangle to restrict drawing to graph bounds
        screen.set_clip(self.rect)

        # Draw background
        pygame.draw.rect(screen, Colors.DARKER_BG.value, self.rect)
        pygame.draw.rect(screen, Colors.BORDER.value, self.rect, 2)

        # Draw edges first (so they appear behind nodes)
        for source, target in self.graph.edges():
            if source in self.pos and target in self.pos:
                start_pos = self._transform_position(self.pos[source])
                end_pos = self._transform_position(self.pos[target])

                # Determine edge color
                if self.selected_edge == (source, target):
                    edge_color = self.selected_color
                else:
                    edge_color = self.edge_color

                # Draw edge
                pygame.draw.line(screen, edge_color, start_pos, end_pos, 2)

                # Draw arrow head
                self._draw_arrow(screen, start_pos, end_pos, edge_color)

                # Draw edge label when zoomed in enough
                if self.zoom >= 1.5:
                    edge_key = (source, target)
                    edge_attrs = self.edge_attributes.get(edge_key, {})
                    rel_type = edge_attrs.get("type", "Unknown")

                    # Calculate midpoint of edge
                    midpoint = (
                        (start_pos[0] + end_pos[0]) / 2,
                        (start_pos[1] + end_pos[1]) / 2,
                    )

                    # Render label text
                    font = self.state.game.cfg.font_tiny
                    text = font.render(rel_type, True, Colors.TEXT.value)
                    text_rect = text.get_rect(
                        center=(int(midpoint[0]), int(midpoint[1]))
                    )
                    screen.blit(text, text_rect)

        # Draw nodes
        for node_id in self.graph.nodes():
            if node_id not in self.pos:
                continue

            pos = self._transform_position(self.pos[node_id])
            attrs = self.node_attributes.get(node_id, {})
            primary_label = attrs.get("primary_label", "Unknown")
            node_name = attrs.get("name", primary_label)

            # Determine color
            if node_id == self.selected_node:
                color = self.selected_color
            elif node_id in self.highlighted_nodes:
                color = self.highlight_color
            else:
                color = self.node_colors.get(primary_label, self.default_node_color)

            # Draw node circle
            radius = int(self.node_radius * self.zoom)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), radius)
            pygame.draw.circle(
                screen, Colors.TEXT_BRIGHT.value, (int(pos[0]), int(pos[1])), radius, 2
            )

            # Draw node label
            if self.zoom > 0.7:  # Only show labels when zoomed in enough
                font = self.state.game.cfg.font_tiny
                text = font.render(node_name, True, Colors.TEXT.value)
                text_rect = text.get_rect(
                    center=(int(pos[0]), int(pos[1]) + radius + 12)
                )
                screen.blit(text, text_rect)

        # Restore the original clipping rectangle
        screen.set_clip(old_clip)

    def _calc_line_angle(self, start, end):
        """Calculate the angle of a line between two points"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return math.atan2(dy, dx)

    def _draw_arrow(self, screen, start, end, color):
        """Draw an arrow head at the end of an edge"""

        angle = self._calc_line_angle(start, end)

        arrow_length = 10
        arrow_angle = math.pi / 6

        # Calculate arrow points
        x1 = end[0] - arrow_length * math.cos(angle - arrow_angle)
        y1 = end[1] - arrow_length * math.sin(angle - arrow_angle)
        x2 = end[0] - arrow_length * math.cos(angle + arrow_angle)
        y2 = end[1] - arrow_length * math.sin(angle + arrow_angle)

        # Draw arrow
        pygame.draw.polygon(screen, color, [end, (x1, y1), (x2, y2)])


def create_graph_visualization(
    state: "GameplayState", graph_rect: pygame.Rect
) -> GraphVisualization:
    """Create and initialize graph visualization for gameplay state

    Args:
        state: The GameplayState instance
        graph_rect: The pygame.Rect defining the graph visualization area
    """
    visualization = GraphVisualization(state, graph_rect)

    # Load graph for current level
    if state.game.current_level:
        visualization.load_graph_for_level(state.game.current_level.level_num)

    return visualization
