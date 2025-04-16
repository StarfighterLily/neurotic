import pygame
import sys
import math
import random

# --- Colors ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREY = (150, 150, 150)
GREEN = (0, 200, 0)
YELLOW = (200, 200, 0) # For temporary connection line

# --- Base Draggable Object Class (Corrected) ---
class DraggableObject:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.id = id(self)

    def handle_event(self, event, global_state=None, connections=None):
        # Basic dragging logic - derived classes will override/extend
        # ... (rest of existing handle_event logic unchanged) ...
        # Make sure recursive calls also pass connections if needed
        handled = False # Example if calling parent's method
        # handled = super().handle_event(event, global_state, connections) # If inheriting handle_event logic
        # ...
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Prevent starting drag if clicking on a node (handled by derived classes)
                # We need a way to check if the click was on a node *before* starting drag
                # This might require passing node rects or checking in derived classes first.
                # For now, derived classes handle node clicks first.
                self.is_dragging = True
                self.drag_offset_x = self.rect.x - event.pos[0]
                self.drag_offset_y = self.rect.y - event.pos[1]
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.rect.x = event.pos[0] + self.drag_offset_x
                self.rect.y = event.pos[1] + self.drag_offset_y
                if hasattr(self, '_update_node_positions') and callable(getattr(self, '_update_node_positions')):
                     self._update_node_positions()
                return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)

    # Removed the conflicting placeholder properties/methods for nodes
    # Derived classes like Perceptron will define their own specific node handling


# --- Default Activation Function (Unchanged) ---
def step_function(x):
    return 1 if x >= 0 else 0

# --- Perceptron Class (Corrected - uses direct attributes now) ---
class Perceptron(DraggableObject):
    def __init__(self, x, y, num_inputs=2, weights=None, bias=None):
        # --- Existing init code ---
        width, height = 60, 80 # Initial size - might need adjustment later if many inputs
        color = GREY
        super().__init__(x, y, width, height, color)
        # Force min 1 input
        self.num_inputs = max(1, num_inputs)

        # --- Weights/Bias/Activation (Existing) ---
        if weights is None:
            # Ensure weight list matches initial num_inputs
            self.weights = [random.uniform(-1, 1) for _ in range(self.num_inputs)]
        else:
            if len(weights) == self.num_inputs: self.weights = weights
            else: raise ValueError(f"Initial weights length ({len(weights)}) != num_inputs ({self.num_inputs})")
        self.bias = random.uniform(-1, 1) if bias is None else bias
        self.activation_function = step_function
        self.output_value = 0
        self.input_values = [0] * self.num_inputs
        # Ensure connections list matches initial num_inputs
        self.input_connections = [None] * self.num_inputs

        # --- Node Radii (Existing) ---
        self.input_node_radius = 5
        self.output_node_radius = 6

        # --- Button Properties ---
        self.button_size = 15 # Size of the square +/- buttons
        self.plus_button_rect = pygame.Rect(0, 0, self.button_size, self.button_size)
        self.minus_button_rect = pygame.Rect(0, 0, self.button_size, self.button_size)
        self.max_inputs = 8 # Set a max limit for sanity
        self.min_inputs = 1 # Minimum 1 input

        # --- Initial node/button position calculation ---
        self.input_nodes_pos = []
        self.output_node_pos = (0, 0)
        self._input_node_rects = []
        self._output_node_rect = pygame.Rect(0,0,0,0)
        self._update_node_positions() # Calculate initial positions for nodes AND buttons

    def _update_node_positions(self):
        """ Calculates the absolute screen positions of connection nodes AND UI buttons. """
        # --- Node Position Update (Existing) ---
        self.input_nodes_pos = []
        # Adjust height slightly if many inputs? For now, fixed height.
        # Consider dynamic height: self.rect.height = max(80, self.num_inputs * 15 + 10)
        input_spacing = self.rect.height / (self.num_inputs + 1)
        for i in range(self.num_inputs):
            node_x = self.rect.left - self.input_node_radius
            node_y = self.rect.top + int(input_spacing * (i + 1))
            self.input_nodes_pos.append((node_x, node_y))
        self.output_node_pos = (self.rect.right + self.output_node_radius, self.rect.centery)
        self._input_node_rects = [ pygame.Rect(
                pos[0] - self.input_node_radius, pos[1] - self.input_node_radius,
                self.input_node_radius * 2, self.input_node_radius * 2
            ) for pos in self.input_nodes_pos ]
        self._output_node_rect = pygame.Rect(
            self.output_node_pos[0] - self.output_node_radius,
            self.output_node_pos[1] - self.output_node_radius,
            self.output_node_radius * 2, self.output_node_radius * 2
        )

        # --- Button Position Update ---
        # Place them near the top-right corner for now
        button_margin = 3
        self.plus_button_rect.topright = (self.rect.right - button_margin, self.rect.top + button_margin)
        self.minus_button_rect.topright = (self.plus_button_rect.left - button_margin, self.rect.top + button_margin)


    # --- Add the getter properties if they were removed ---
    @property
    def output_node_rect(self):
         return self._output_node_rect

    def get_input_node_rect(self, index):
        if 0 <= index < len(self._input_node_rects):
            return self._input_node_rects[index]
        return None

    # handle_event, calculate_output, draw methods remain the same as before
    # Make sure they internally reference self.output_node_pos, self.input_nodes_pos, etc. directly
    # (They already did, so they should be fine)
    def handle_event(self, event, global_state, connections=None):
        # --- Check Button Clicks FIRST ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left-click only
            # Check '+' Button
            if self.plus_button_rect.collidepoint(event.pos):
                if self.num_inputs < self.max_inputs:
                    print(f"Perceptron {self.id}: Increasing inputs to {self.num_inputs + 1}")
                    self.num_inputs += 1
                    self.weights.append(random.uniform(-1, 1)) # Add new random weight
                    self.input_connections.append(None)
                    self.input_values.append(0) # Match input_values list size
                    self._update_node_positions()
                    return True # Handled
                else:
                    print(f"Perceptron {self.id}: Max inputs ({self.max_inputs}) reached.")
                    return True # Handled (consumed click)

            # Check '-' Button
            elif self.minus_button_rect.collidepoint(event.pos):
                if self.num_inputs > self.min_inputs:
                    print(f"Perceptron {self.id}: Decreasing inputs to {self.num_inputs - 1}")
                    self.num_inputs -= 1
                    # Remove last weight and connection slot
                    self.weights.pop()
                    removed_connection_source = self.input_connections.pop()
                    self.input_values.pop() # Match input_values list size

                    # *** IMPORTANT: Remove any connection from global list ***
                    if removed_connection_source is not None and connections is not None:
                        target_input_index_removed = self.num_inputs # Index that was removed
                        for idx in range(len(connections) - 1, -1, -1):
                             conn = connections[idx]
                             # Check if this connection was the one going to the removed input slot
                             if conn['target_obj'] == self and conn['target_input_idx'] == target_input_index_removed:
                                  connections.pop(idx)
                                  print(f"  Removed connection from global list for input {target_input_index_removed}")
                                  break # Found and removed

                    self._update_node_positions()
                    return True # Handled
                else:
                    print(f"Perceptron {self.id}: Min inputs ({self.min_inputs}) reached.")
                    return True # Handled (consumed click)

        # --- If no button was clicked, proceed with existing node/drag/right-click logic ---
        drag_handled = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # --- Right-click for deleting (Existing) ---
            if event.button == 3:
                for i, rect in enumerate(self._input_node_rects):
                    if rect.collidepoint(event.pos):
                        # ... (existing right-click removal logic) ...
                        if self.input_connections[i] is not None:
                            self.input_connections[i] = None
                            if connections is not None:
                                 for idx in range(len(connections) - 1, -1, -1):
                                     conn = connections[idx]
                                     if conn['target_obj'] == self and conn['target_input_idx'] == i:
                                         connections.pop(idx)
                                         break
                            return True
                        else: return True # Handled click
                # Pass - allow other handling if not on node

            # --- Left-click (Nodes or Drag) ---
            elif event.button == 1:
                # Check output node (Existing)
                if hasattr(self, '_output_node_rect') and self._output_node_rect.collidepoint(event.pos):
                    # ... (start connection logic) ...
                    global_state['is_drawing_connection'] = True
                    global_state['connection_start_obj'] = self
                    global_state['connection_start_pos'] = self.output_node_pos
                    return True
                # Check input nodes (Existing)
                if not global_state.get('is_drawing_connection'):
                    for i, rect in enumerate(self._input_node_rects):
                        if rect.collidepoint(event.pos):
                            return True # Consume click
                # Check body drag (Existing) - This is now only reached if no button/node was hit
                if self.rect.collidepoint(event.pos):
                    self.is_dragging = True
                    self.drag_offset_x = self.rect.x - event.pos[0]
                    self.drag_offset_y = self.rect.y - event.pos[1]
                    return True

        # --- Drag Handling (Existing) ---
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_dragging and event.button == 1: # Check button
                self.is_dragging = False
                drag_handled = True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.rect.x = event.pos[0] + self.drag_offset_x
                self.rect.y = event.pos[1] + self.drag_offset_y
                self._update_node_positions()
                drag_handled = True

        return drag_handled


    def calculate_output(self):
        current_inputs = []
        for i in range(self.num_inputs):
             # Check index bounds for safety
             if i < len(self.input_connections):
                  source_obj = self.input_connections[i]
                  if source_obj:
                      current_inputs.append(getattr(source_obj, 'output_value', 0))
                  else:
                      current_inputs.append(0)
             else:
                  current_inputs.append(0) # Append 0 if index out of bounds

        self.input_values = current_inputs
        # Ensure weights list matches input values length before zip
        if len(self.weights) != len(self.input_values):
             print(f"Warning: Weight count ({len(self.weights)}) != Input count ({len(self.input_values)}) in Perceptron {self.id}. Recalculating.")
             # Adjust weights list - might need better strategy
             # For now, pad with 0 or truncate
             self.weights = self.weights[:len(self.input_values)] + [0.0] * (len(self.input_values) - len(self.weights))


        weighted_sum = sum(w * i for w, i in zip(self.weights, self.input_values)) + self.bias
        self.output_value = self.activation_function(weighted_sum)


    def draw(self, surface):
        # --- Draw Body and Nodes (Existing) ---
        body_color = GREEN if self.output_value == 1 else GREY
        pygame.draw.rect(surface, body_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        # Input nodes
        for i, pos in enumerate(self.input_nodes_pos):
            pygame.draw.circle(surface, BLACK, pos, self.input_node_radius)
            if i < len(self.input_values):
                 in_val = self.input_values[i]
                 inner_color = GREEN if in_val == 1 else WHITE
                 pygame.draw.circle(surface, inner_color, pos, self.input_node_radius - 2)
            else: pygame.draw.circle(surface, WHITE, pos, self.input_node_radius - 2)
        # Output node
        pygame.draw.circle(surface, BLACK, self.output_node_pos, self.output_node_radius)
        inner_color = GREEN if self.output_value == 1 else WHITE
        pygame.draw.circle(surface, inner_color, self.output_node_pos, self.output_node_radius - 2)

        # --- Draw +/- Buttons ---
        button_color = (100, 100, 200) # A blue-ish color for buttons
        pygame.draw.rect(surface, button_color, self.plus_button_rect, border_radius=2)
        pygame.draw.rect(surface, button_color, self.minus_button_rect, border_radius=2)
        # Draw borders
        pygame.draw.rect(surface, WHITE, self.plus_button_rect, 1, border_radius=2)
        pygame.draw.rect(surface, WHITE, self.minus_button_rect, 1, border_radius=2)

        # Draw '+' and '-' symbols (requires pygame.font initialized)
        if 'font' in globals(): # Basic check if font exists
             plus_surf = font.render('+', True, WHITE)
             minus_surf = font.render('-', True, WHITE)
             plus_rect = plus_surf.get_rect(center=self.plus_button_rect.center)
             minus_rect = minus_surf.get_rect(center=self.minus_button_rect.center)
             surface.blit(plus_surf, plus_rect)
             surface.blit(minus_surf, minus_rect)

class Switch(DraggableObject):
    def __init__(self, x, y):
        width, height = 40, 40
        color = RED # Start in 'off' state
        super().__init__(x, y, width, height, color)
        self.output_value = 0 # 0 for off, 1 for on
        self.output_node_radius = 6

        # --- Define Toggle Area ---
        # Make it slightly smaller and centered within the main rect
        toggle_margin = 8
        self.toggle_rect = pygame.Rect(
            self.rect.left + toggle_margin,
            self.rect.top + toggle_margin,
            self.rect.width - 2 * toggle_margin,
            self.rect.height - 2 * toggle_margin
        )
        # Color for the toggle button itself
        self.toggle_button_color = BLACK

        self._update_node_positions() # Calculate initial node & update toggle rect pos

    def _update_node_positions(self):
        """ Calculates the absolute screen positions of connection nodes AND toggle area. """
        # Output node centered vertically on the right edge
        self.output_node_pos = (self.rect.right + self.output_node_radius, self.rect.centery)
        self._output_node_rect = pygame.Rect(
            self.output_node_pos[0] - self.output_node_radius,
            self.output_node_pos[1] - self.output_node_radius,
            self.output_node_radius * 2, self.output_node_radius * 2
        )
        # Update toggle area position relative to the main rect's current position
        toggle_margin = 8
        self.toggle_rect.topleft = (self.rect.left + toggle_margin, self.rect.top + toggle_margin)


    @property
    def output_node_rect(self):
         return self._output_node_rect

    # Add connections param default None
    def handle_event(self, event, global_state, connections=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # --- Check Nodes First (Unaffected by toggle/drag distinction) ---
            if hasattr(self, '_output_node_rect') and self._output_node_rect.collidepoint(event.pos):
                 # Start connection (Left-click only)
                 if event.button == 1:
                      print(f"Clicked output node of switch {self.id}")
                      global_state['is_drawing_connection'] = True
                      global_state['connection_start_obj'] = self
                      global_state['connection_start_pos'] = self.output_node_pos
                      return True # Handled

            # --- Left Click Logic (Check Toggle vs Drag) ---
            elif event.button == 1: # Left mouse button
                 # 1. Check Toggle Area FIRST
                 if self.toggle_rect.collidepoint(event.pos):
                      # Only toggle if not currently drawing a connection from elsewhere
                      if not global_state.get('is_drawing_connection'):
                           print(f"Toggling switch {self.id} via toggle area")
                           self.output_value = 1 - self.output_value
                           # Update color based on state (handled in draw)
                           return True # Handled state toggle
                 # 2. Check Rest of the Body for Drag
                 elif self.rect.collidepoint(event.pos):
                      # Click was inside main body but *not* the toggle area
                      print(f"Starting drag for switch {self.id}")
                      self.is_dragging = True
                      self.drag_offset_x = self.rect.x - event.pos[0]
                      self.drag_offset_y = self.rect.y - event.pos[1]
                      return True # Handled drag start

            # --- Right Click Logic (Could add functionality later if needed) ---
            elif event.button == 3:
                 # Allow right-click on body to potentially select/inspect later?
                 # For now, maybe just consume the click if it's on the body
                 if self.rect.collidepoint(event.pos):
                     print(f"Right-clicked switch {self.id}")
                     return True # Consume right-click on body

        # --- Mouse Button Up (Stop Drag) ---
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging: # Check button if needed
                self.is_dragging = False
                print(f"Stopped drag for switch {self.id}")
                return True

        # --- Mouse Motion (Update Drag) ---
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.rect.x = event.pos[0] + self.drag_offset_x
                self.rect.y = event.pos[1] + self.drag_offset_y
                self._update_node_positions() # IMPORTANT: Keep toggle rect position updated!
                return True

        return False # Event not handled


    def draw(self, surface):
        """ Draws the switch body, toggle area, and output node. """
        # Update body color based on state
        body_color = GREEN if self.output_value == 1 else RED
        # Draw the main body
        pygame.draw.rect(surface, body_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1) # Border

        # --- Draw the Toggle Area ---
        pygame.draw.rect(surface, self.toggle_button_color, self.toggle_rect)
        # Add a small border to toggle area for visibility
        pygame.draw.rect(surface, WHITE, self.toggle_rect, 1)

        # --- Draw Output Node ---
        if hasattr(self, 'output_node_pos'): # Check exists
            pygame.draw.circle(surface, BLACK, self.output_node_pos, self.output_node_radius)
            inner_color = GREEN if self.output_value == 1 else WHITE
            pygame.draw.circle(surface, inner_color, self.output_node_pos, self.output_node_radius - 2)
        
# --- Light Class ---
class Light(DraggableObject):
    def __init__(self, x, y):
        radius = 20 # Make it circular visually
        # Position rect based on center for easier circle drawing
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, GREY)
        self.radius = radius
        self.input_value = 0 # Value received from connection
        self.num_inputs = 1 # Lights only have one input
        self.input_connections = [None] * self.num_inputs
        self.input_node_radius = 5
        self._update_node_positions() # Calculate initial node position

    def _update_node_positions(self):
        """ Calculates the absolute screen positions of connection nodes. """
        # Input node centered vertically on the left edge
        node_x = self.rect.left - self.input_node_radius
        node_y = self.rect.centery
        self.input_nodes_pos = [(node_x, node_y)] # Store as list for consistency

        # Calculate clickable area (Rect) for the node
        self._input_node_rects = [
            pygame.Rect(
                pos[0] - self.input_node_radius, pos[1] - self.input_node_radius,
                self.input_node_radius * 2, self.input_node_radius * 2
            ) for pos in self.input_nodes_pos
        ]

    def get_input_node_rect(self, index):
         # Provide access for connection logic (only index 0 is valid)
        if index == 0 and self._input_node_rects:
             return self._input_node_rects[0]
        return None

    def handle_event(self, event, global_state, connections=None):
        # --- Dragging Logic (Call Parent) ---
        # Use super() properly if DraggableObject.handle_event contains useful base logic
        drag_handled = super().handle_event(event, global_state, connections)
        if drag_handled:
             return True

        # --- Node Click Handling ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            node_rect = self.get_input_node_rect(0) # Lights only have input 0
            if node_rect and node_rect.collidepoint(event.pos):
                # --- Right-click for deleting connection ---
                if event.button == 3: # Right mouse button
                    print(f"Right-clicked input node of light {self.id}")
                    if self.input_connections[0] is not None:
                        print(f"  Removing connection to light input")
                        self.input_connections[0] = None
                        # Remove from global list
                        for idx in range(len(connections) - 1, -1, -1):
                            conn = connections[idx]
                            if conn['target_obj'] == self and conn['target_input_idx'] == 0:
                                connections.pop(idx)
                                print(f"  Removed connection entry from global list.")
                                break
                        return True # Handled removal
                    else:
                        print(f"  Light input is not connected.")
                        return True # Handled click
                # --- Left-click (potential connection end, consume click) ---
                elif event.button == 1:
                     if not global_state.get('is_drawing_connection'):
                          print(f"Clicked input node of light {self.id}")
                          return True # Consume click

        return False # Event not handled by specific light logic

    def update_state(self):
         """ Updates the light's input value based on its connection. """
         source_obj = self.input_connections[0]
         if source_obj:
             # Use getattr for safety, default to 0 if no output_value
             self.input_value = getattr(source_obj, 'output_value', 0)
         else:
             self.input_value = 0 # No connection, input is 0

    def draw(self, surface):
        """ Draws the light body and its input node. """
        # Determine color based on input value
        light_color = YELLOW if self.input_value == 1 else GREY

        # Draw the main body (circle)
        # Use rect.center for consistent positioning
        pygame.draw.circle(surface, light_color, self.rect.center, self.radius)
        pygame.draw.circle(surface, BLACK, self.rect.center, self.radius, 1) # Border

        # Draw input node (only one)
        if self.input_nodes_pos:
            pos = self.input_nodes_pos[0]
            pygame.draw.circle(surface, BLACK, pos, self.input_node_radius)
            # Indicate input value state
            inner_color = GREEN if self.input_value == 1 else WHITE
            pygame.draw.circle(surface, inner_color, pos, self.input_node_radius - 2)


# --- Main loop and remaining code ---
# --- Initialization ---
pygame.init()
pygame.font.init() # Initialize font module
font = pygame.font.SysFont(None, 18) # Use a small font size for buttons

# --- Screen Setup ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Perceptron Playground - Inputs & Outputs")

# --- Create Objects ---
# Add Switches and Lights alongside Perceptrons
switch1 = Switch(50, 50)
switch2 = Switch(50, 150)
perceptron1 = Perceptron(200, 100, num_inputs=2)
perceptron2 = Perceptron(400, 200, num_inputs=1)
light1 = Light(600, 100)
light2 = Light(600, 250)


all_objects = [switch1, switch2, perceptron1, perceptron2, light1, light2] # Add new objects
connections = []

# --- Global State for Connection Drawing (Unchanged) ---
global_connection_state = {
    'is_drawing_connection': False,
    'connection_start_obj': None,
    'connection_start_pos': None,
}

# --- Game Loop ---
running = True
clock = pygame.time.Clock()

while running:
    mouse_pos = pygame.mouse.get_pos()

    # --- Event Handling ---
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        handled_by_ui = False
        # Global MOUSEBUTTONUP for finalizing connections (Unchanged)
        if event.type == pygame.MOUSEBUTTONUP and global_connection_state['is_drawing_connection']:
            # ... (existing connection finalization logic unchanged) ...
            handled_by_ui = True # Make sure this is set
            start_obj = global_connection_state['connection_start_obj']
            # ... find target ...
            target_found = False
            for obj in all_objects:
                if isinstance(obj, (Perceptron, Light)):
                     for i in range(getattr(obj, 'num_inputs', 0)):
                          input_rect = None
                          if hasattr(obj, 'get_input_node_rect') and callable(getattr(obj, 'get_input_node_rect')):
                              input_rect = obj.get_input_node_rect(i)
                          if input_rect and input_rect.collidepoint(event.pos):
                              target_obj = obj
                              target_input_index = i
                              print(f"Connection success: Obj {start_obj.id} output -> Obj {target_obj.id} input {target_input_index}")
                              # ... (update target_obj.input_connections and global connections list) ...
                              if hasattr(target_obj, 'input_connections') and target_input_index < len(target_obj.input_connections):
                                   if target_obj.input_connections[target_input_index] is not None: print("Warning: Input node already connected. Overwriting.")
                                   target_obj.input_connections[target_input_index] = start_obj
                              else: print(f"Error: Target object {target_obj.id} missing or has invalid input_connections.")
                              # Add/Update global list
                              existing_conn_idx = -1
                              for idx, conn in enumerate(connections):
                                   if conn['target_obj'] == target_obj and conn['target_input_idx'] == target_input_index:
                                       existing_conn_idx = idx
                                       break
                              if existing_conn_idx != -1: connections[existing_conn_idx]['source_obj'] = start_obj
                              else: connections.append({'source_obj': start_obj, 'target_obj': target_obj, 'target_input_idx': target_input_index})
                              target_found = True
                              break
                if target_found: break
            if not target_found: print("Connection cancelled.")
            # Reset global state
            global_connection_state['is_drawing_connection'] = False
            global_connection_state['connection_start_obj'] = None
            global_connection_state['connection_start_pos'] = None


        # --- Pass events to objects if not handled globally ---
        if not handled_by_ui:
            for obj in reversed(all_objects):
                if hasattr(obj, 'handle_event') and callable(getattr(obj, 'handle_event')):
                    # *** MODIFIED: Pass connections list ***
                    if obj.handle_event(event, global_connection_state, connections):
                        handled_by_ui = True
                        break

    # --- Update State (Unchanged) ---
    # 1. Update Perceptrons
    for obj in all_objects:
        if isinstance(obj, Perceptron): obj.calculate_output()
    # 2. Update Lights
    for obj in all_objects:
        if isinstance(obj, Light): obj.update_state()

    # --- Drawing (Unchanged) ---
    screen.fill(WHITE)
    # Draw established connections
    for conn in connections:
        # ... (existing connection drawing logic) ...
        source = conn['source_obj']
        target = conn['target_obj']
        target_idx = conn['target_input_idx']
        start_pos = getattr(source, 'output_node_pos', None)
        end_pos = None
        target_input_nodes = getattr(target, 'input_nodes_pos', None)
        if target_input_nodes and 0 <= target_idx < len(target_input_nodes):
            end_pos = target_input_nodes[target_idx]
        if start_pos and end_pos:
            pygame.draw.line(screen, BLUE, start_pos, end_pos, 2)
    # Draw temporary connection line
    if global_connection_state['is_drawing_connection'] and global_connection_state['connection_start_pos']:
        start_pos = global_connection_state['connection_start_pos']
        pygame.draw.line(screen, YELLOW, start_pos, mouse_pos, 2)
    # Draw all objects
    for obj in all_objects:
        if hasattr(obj, 'draw') and callable(getattr(obj, 'draw')): obj.draw(screen)

    # --- Update Display ---
    pygame.display.flip()
    clock.tick(60)

# --- Cleanup (Unchanged) ---
pygame.font.quit()
pygame.quit()
sys.exit()