"""
Oscilloscope trigger detection and management.

This module provides trigger detection logic for the oscilloscope tab.
"""

import time
from ..i18n import t

class OscTrigger:
    """Handles oscilloscope trigger detection and logic."""
    
    def __init__(self, data_tab, trigger_source, trigger_level, trigger_edge, trigger_mode):
        self.data_tab = data_tab
        self.trigger_source = trigger_source
        self.trigger_level = trigger_level
        self.trigger_edge = trigger_edge
        self.trigger_mode = trigger_mode
        
        # Trigger state
        self.last_sample_value = None
        self.is_armed = False
        self.is_triggered = False
        self.arm_start_time = None
        self.trigger_point_index = -1
    
    def arm(self):
        """Arm the trigger for detection."""
        self.is_armed = True
        self.is_triggered = False
        self.last_sample_value = None
        self.arm_start_time = time.time()
    
    def disarm(self):
        """Disarm the trigger."""
        self.is_armed = False
        self.is_triggered = False
        self.last_sample_value = None
    
    def check_trigger_conditions(self):
        """Check if trigger conditions are met."""
        if not self.is_armed:
            return False
            
        try:
            # Get current data from data tab
            data_lines = self.data_tab.get_data()
            if not data_lines:
                return False
            
            # Get trigger settings
            trigger_col = int(self.trigger_source.get_value()) - 1
            trigger_level = float(self.trigger_level.get_value())
            trigger_edge = self.trigger_edge.get_value()
            
            # Get the latest sample
            latest_line = data_lines[-1]
            try:
                values = latest_line.split()
                if trigger_col < len(values):
                    current_value = float(values[trigger_col])
                    
                    # Check for trigger condition
                    if self.last_sample_value is not None:
                        triggered = self._check_edge_condition(
                            self.last_sample_value, current_value, trigger_level, trigger_edge
                        )
                        
                        if triggered and not self.is_triggered:
                            self._trigger_detected(data_lines)
                            return True
                    
                    self.last_sample_value = current_value
                    
            except (ValueError, IndexError):
                pass  # Skip invalid data lines
                
        except Exception as e:
            print(t("ui.osc_tab.trigger_monitoring_error", error=str(e)))
            
        return False
    
    def _check_edge_condition(self, last_value, current_value, trigger_level, trigger_edge):
        """Check if edge condition is met."""
        # Compare with translated trigger edge values using i18n keys
        if trigger_edge == t("ui.osc_tab.trigger_edges.rising"):
            return (last_value <= trigger_level < current_value)
        elif trigger_edge == t("ui.osc_tab.trigger_edges.falling"): 
            return (last_value >= trigger_level > current_value)
        elif trigger_edge == t("ui.osc_tab.trigger_edges.both"):
            return ((last_value <= trigger_level < current_value) or 
                   (last_value >= trigger_level > current_value))
        return False
    
    def _trigger_detected(self, data_lines):
        """Handle trigger detection."""
        self.is_triggered = True
        # Simply remember where we are in the data buffer right now
        self.trigger_point_index = len(data_lines)  # Data after this point is what we want
    
    def get_trigger_point_index(self):
        """Get the index where trigger was detected."""
        return self.trigger_point_index
    
    def reset_trigger_state(self):
        """Reset trigger detection state."""
        self.last_sample_value = None
        self.is_triggered = False
