# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockInventoryReport(models.AbstractModel):
    _name = 'report.z_stock.report_stock_inventory'
    _description = 'Báo Cáo Kho Đầu Kỳ Cuối Kỳ'

    @api.model
    def _get_report_values(self, docids, data=None):
        print(docids, data)
        wizard = self.env['stock.inventory.report.wizard'].browse(docids)
        print(wizard)
        if wizard:
            # Tính toán lại dữ liệu từ wizard để tránh URL quá dài
            report_data = wizard._prepare_report_data()
            return {
                'doc_ids': docids,
                'doc_model': 'stock.inventory.report.wizard',
                'docs': wizard,
                'date_from': wizard.date_from,
                'date_to': wizard.date_to,
                'location_id': wizard.location_id.display_name,
                'opening_stock': report_data.get('opening_stock', []),
                'incoming_stock': report_data.get('incoming_stock', []),
                'outgoing_stock': report_data.get('outgoing_stock', []),
                'closing_stock': report_data.get('closing_stock', []),
                'current_time': fields.Datetime.now().strftime('%d/%m/%Y %H:%M'),
            }
        else:
            return {
                'doc_ids': docids,
                'doc_model': 'stock.inventory.report.wizard',
                'docs': self.env['stock.inventory.report.wizard'].browse(docids),
                'date_from': '',
                'date_to': '',
                'location_id': '',
                'opening_stock': [],
                'incoming_stock': [],
                'outgoing_stock': [],
                'closing_stock': [],
                'current_time': fields.Datetime.now().strftime('%d/%m/%Y %H:%M'),
            }
