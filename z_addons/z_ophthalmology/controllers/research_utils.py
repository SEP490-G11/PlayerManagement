import pytz
from datetime import datetime, timedelta
from odoo import _

from odoo.addons.z_web.helpers.constants import (
    TIME_ZONE,
    DEFAULT_DATE_TIME_FORMAT,
    STANDARD_DATE_FORMAT,
    STANDARD_TIME_FORMAT,
    TIME_SLOT_FORMAT,
)
from odoo.exceptions import ValidationError


class ZResearchUtils:
    @staticmethod
    def calculate_ocular_axial_length_gm_radius_of_curvature( eyeball_axis_length: float , steep_or_flat_k: float, age: int):
        axis_eye_point = 0
        ocular_axial_radius = 0
        steep_or_flat_k_mm = 0
        if  steep_or_flat_k  != 0:
         steep_or_flat_k_mm = round(
                    337.5 / steep_or_flat_k, 3
                )
        if steep_or_flat_k != 0:
            ocular_axial_radius = round(eyeball_axis_length/steep_or_flat_k_mm, 3)
        if 6 <= age <=8:
            axis_eye_point = ZResearchUtils.compute_score_for_six_to_eight(eyeball_axis_length)
        elif age <= 10:
            axis_eye_point = ZResearchUtils.compute_score_for_nine_to_ten(eyeball_axis_length)
        return steep_or_flat_k_mm, ocular_axial_radius, axis_eye_point,

    @staticmethod
    def compute_score_for_six_to_eight( length: float):
        if length < 22.93:
            point = 0
        elif length <= 23.11:
            point = 1
        elif length <= 23.18:
            point = 2
        else:
            point = 3
            
        return point
    
    @staticmethod
    def compute_score_for_nine_to_ten(length: float):
        if length < 23.33:
            point = 0
        elif length <= 23.61:
            point = 1
        else:
            point = 2
        return point
    
    @staticmethod
    def compute_score_family_history_of_myopia(value , age : int):
            point = None
            string_vls = None
            if 6 <= age <=8:
                if value == "1":
                    string_vls= _("No Body")
                    point = 0
                elif value == "2":
                    string_vls = _("Parents")
                    point = 2
                elif value == "3":
                    string_vls = _("Both")
                    point = 3
            if 9 <= age <= 10: 
                if value == "1":
                    string_vls= _("No Body")
                    point = 0
                elif value == "2":
                    string_vls = _("Parents")
                    point = 1
                elif value == "3":
                    string_vls = _("Both")
                    point = 2
            return point, string_vls
    
    @staticmethod
    def check_pl_or_number(value):
        try:
            float_value = float(value)
        except ValueError:
            if value.lower() == "pl":
                return 'The input is the string "pl".'
            else:
                raise ValidationError(_('Invalid value'))
    

    @staticmethod
    def compute_myopia_refractive_error__value(pre, post):
        if isinstance(pre, str) and pre.lower() == "pl":
            pre = 0
        if isinstance(post, str) and post.lower() == "pl":
            post = 0
        if post is not False:
            return post
        else:
            return pre
   
    @staticmethod
    def compute_pre_myopia_refractive_error_right_eye_point(value, is_post, is_pre, age ):
        is_six_to_age =  6 <= age <= 8
        is_nine_to_ten = 9 <= age <= 10
        
        if is_post and is_six_to_age:  
            if float(value) > 1:
                return 0
            elif float(value) >= 0.75:
                return 2
            else:
                return 3
        if is_pre and is_six_to_age:
            if float(value) > 0.75:
                return 0
            elif float(value) >= 0.32:
                return 2
            else:
                return 3
        if is_post and is_nine_to_ten:  
            if float(value) > 0.875:
                return 0
            elif float(value) >= 0.375:
                return 1
            else:
                return 2
        if is_pre and is_nine_to_ten:
            if float(value) > 0.625:
                return 0
            elif float(value) >= 0.125:
                return 1
            else:
                return 2
        return None 
    
    @staticmethod
    def sum_if_num(a,b):
        if  not a  or not b:    
            return 0
        return round((a + b)/2,3) 
