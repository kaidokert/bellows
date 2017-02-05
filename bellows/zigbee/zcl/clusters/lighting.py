"""Lighting Functional Domain"""

import bellows.types as t
from bellows.zigbee.zcl import Cluster


class Color(Cluster):
    """Attributes and commands for controlling the color
    properties of a color-capable light"""
    cluster_id = 0x0300
    name = 'Color Control'
    attributes = {
        # Color Information
        0x0000: ('current_hue', t.uint8_t),
        0x0001: ('current_saturation', t.uint8_t),
        0x0002: ('remaining_time', t.uint16_t),
        0x0003: ('current_x', t.uint16_t),
        0x0004: ('current_y', t.uint16_t),
        0x0005: ('drift_compensation', t.uint8_t),  # enum8
        0x0006: ('compensation_text', t.LVBytes),
        0x0007: ('color_temperature', t.uint16_t),
        0x0008: ('color_mode', t.uint8_t),  # enum8
        # Defined Primaries Information
        0x0010: ('num_primaries', t.uint8_t),
        0x0011: ('primary1_x', t.uint16_t),
        0x0012: ('primary1_y', t.uint16_t),
        0x0013: ('primary1_intensity', t.uint8_t),
        0x0015: ('primary2_x', t.uint16_t),
        0x0016: ('primary2_y', t.uint16_t),
        0x0017: ('primary2_intensity', t.uint8_t),
        0x0019: ('primary3_x', t.uint16_t),
        0x001a: ('primary3_y', t.uint16_t),
        0x001b: ('primary3_intensity', t.uint8_t),
        # Additional Defined Primaries Information
        0x0020: ('primary4_x', t.uint16_t),
        0x0021: ('primary4_y', t.uint16_t),
        0x0022: ('primary4_intensity', t.uint8_t),
        0x0024: ('primary5_x', t.uint16_t),
        0x0025: ('primary5_y', t.uint16_t),
        0x0026: ('primary5_intensity', t.uint8_t),
        0x0028: ('primary6_x', t.uint16_t),
        0x0029: ('primary6_y', t.uint16_t),
        0x002a: ('primary6_intensity', t.uint8_t),
        # Defined Color Point Settings
        0x0030: ('white_point_x', t.uint16_t),
        0x0031: ('white_point_y', t.uint16_t),
        0x0032: ('color_point_r_x', t.uint16_t),
        0x0033: ('color_point_r_y', t.uint16_t),
        0x0034: ('color_point_r_intensity', t.uint8_t),
        0x0036: ('color_point_g_x', t.uint16_t),
        0x0037: ('color_point_g_y', t.uint16_t),
        0x0038: ('color_point_g_intensity', t.uint8_t),
        0x003a: ('color_point_b_x', t.uint16_t),
        0x003b: ('color_point_b_y', t.uint16_t),
        0x003c: ('color_point_b_intensity', t.uint8_t),
        # ...
        0x4000: ('enhanced_current_hue', t.uint16_t),
        0x4001: ('enhanced_color_mode', t.uint8_t),  # enum8
        0x4002: ('color_loop_active', t.uint8_t),
        0x4003: ('color_loop_direction', t.uint8_t),
        0x4004: ('color_loop_time', t.uint16_t),
        0x4005: ('color_loop_start_enhanced_hue', t.uint16_t),
        0x4006: ('color_loop_stored_enhanced_hue', t.uint16_t),
        0x400a: ('color_capabilities', t.uint16_t),
        0x400b: ('color_temp_physical_min', t.uint16_t),
        0x400c: ('color_temp_physical_max', t.uint16_t),
    }
    server_commands = {
        0x0000: ('move_to_hue', (), False),
        0x0001: ('move_hue', (), False),
        0x0002: ('step_hue', (), False),
        0x0003: ('move_to_saturation', (), False),
        0x0004: ('move_saturation', (), False),
        0x0005: ('step_saturation', (), False),
        0x0006: ('move_to_hue_and_saturation', (), False),
        0x0007: ('move_to_color', (), False),
        0x0008: ('move_color', (), False),
        0x0009: ('step_color', (), False),
        0x000a: ('move_to_color_temp', (), False),
        0x0040: ('enhanced_move_to_hue', (), False),
        0x0041: ('enhanced_move_hue', (), False),
        0x0042: ('enhanced_step_hue', (), False),
        0x0043: ('enhanced_move_to_hue_and_saturation', (), False),
        0x0044: ('color_loop_set', (), False),
        0x0047: ('stop_move_step', (), False),
    }
    client_commands = {}


class Ballast(Cluster):
    """Attributes and commands for configuring a lighting
    ballast"""
    cluster_id = 0x0301
    attributes = {
        # Ballast Information
        0x0000: ('physical_min_level', t.uint8_t),
        0x0001: ('physical_max_level', t.uint8_t),
        0x0002: ('ballast_status', t.uint8_t),  # bitmap8
        # Ballast Settings
        0x0010: ('min_level', t.uint8_t),
        0x0011: ('max_level', t.uint8_t),
        0x0012: ('power_on_level', t.uint8_t),
        0x0013: ('power_on_fade_time', t.uint16_t),
        0x0014: ('intrinsic_ballast_factor', t.uint8_t),
        0x0015: ('ballast_factor_adjustment', t.uint8_t),
        # Lamp Information
        0x0020: ('lamp_quantity', t.uint8_t),
        # Lamp Settings
        0x0030: ('lamp_type', t.LVBytes),
        0x0031: ('lamp_manufacturer', t.LVBytes),
        0x0032: ('lamp_rated_hours', t.uint24_t),
        0x0033: ('lamp_burn_hours', t.uint24_t),
        0x0034: ('lamp_alarm_mode', t.uint8_t),  # bitmap8
        0x0035: ('lamp_burn_hours_trip_point', t.uint24_t),
    }
    server_commands = {}
    client_commands = {}
