

import json
import logging
import requests
import urllib.parse
from odoo.addons.z_web.helpers.utils import ZUtils
from odoo.addons.z_zns.helpers.constants import BASE_URL
from odoo.addons.z_web.helpers.constants import READABLE_DATE_FORMAT
import datetime

_logger = logging.getLogger(__name__)


class ZInvoiceUtils:
    @staticmethod
    def convert_number_to_vietnamese(n):
        chu_so = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
        hang_don_vi = ["", "nghìn", "triệu", "tỷ"]

        def doc_3_chu_so(so, is_first_group):
            tram = so // 100
            chuc = (so % 100) // 10
            don_vi = so % 10
            ket_qua = ""

            if tram > 0:
                ket_qua += chu_so[tram] + " trăm"
                if chuc == 0 and don_vi > 0:
                    ket_qua += " linh"
            elif not is_first_group: 
                ket_qua += "không trăm"
                if chuc == 0 and don_vi > 0:
                    ket_qua += " linh"

            if chuc > 1:
                ket_qua += " " + chu_so[chuc] + " mươi"
                if don_vi == 1:
                    ket_qua += " mốt"
                elif don_vi == 5:
                    ket_qua += " lăm"
                elif don_vi > 0:
                    ket_qua += " " + chu_so[don_vi]
            elif chuc == 1:
                ket_qua += " mười"
                if don_vi == 5:
                    ket_qua += " lăm"
                elif don_vi > 0:
                    ket_qua += " " + chu_so[don_vi]
            elif don_vi > 0:
                ket_qua += " " + chu_so[don_vi]

            return ket_qua.strip()
        
        if n == 0:
            return "không"

        parts = []
        i = 0
        while n > 0:
            so = n % 1000
            if so > 0:
                is_first_group = (i == 0)
                parts.append(doc_3_chu_so(so, is_first_group) + " " + hang_don_vi[i])
            n = n // 1000
            i += 1

        return ', '.join(reversed(parts)).strip()
