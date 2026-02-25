# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class StockInventoryReportWizard(models.TransientModel):
    _name = 'stock.inventory.report.wizard'
    _description = 'Wizard Báo Cáo Kho Đầu Kỳ Cuối Kỳ'

    date_from = fields.Datetime(
        string='Từ ngày',
        required=True,
        default=lambda self: fields.Datetime.context_timestamp(self, fields.Datetime.now()).replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    )
    date_to = fields.Datetime(
        string='Đến ngày',
        required=True,
        default=lambda self: fields.Datetime.context_timestamp(self, fields.Datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None))
    location_id = fields.Many2one(
        'stock.location',
        string='Kho',
        required=True,
        default=False
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise UserError('Thời gian bắt đầu không thể lớn hơn thời gian kết thúc!')

    def action_generate_report(self):
        self.ensure_one()
        
        # Gọi action để hiển thị báo cáo dưới dạng HTML
        # Chỉ truyền ID của wizard, không truyền data để tránh URL quá dài
        return self.env.ref('z_stock.action_report_stock_inventory').report_action(
            self, config=False
        )
    
    def action_export_excel(self):
        """Xuất báo cáo ra Excel"""
        self.ensure_one()
        
        # Chuẩn bị dữ liệu cho báo cáo
        report_data = self._prepare_report_data()
        
        # Tạo file Excel
        import base64
        import io
        import xlsxwriter
        
        # Tạo workbook và worksheet
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output)
        ws = wb.add_worksheet("Báo cáo kho")
        
        # Định nghĩa formats
        header_format = wb.add_format({
            'bold': True,
            'color': 'white',
            'bg_color': '#343A40',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        sub_header_format = wb.add_format({
            'bold': True,
            'color': 'white',
            'bg_color': '#495057',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        title_format = wb.add_format({
            'bold': True,
            'size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        center_format = wb.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        right_format = wb.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'
        })
        
        text_format = wb.add_format({
            'border': 1,
            'valign': 'vcenter'
        })
        
        total_format = wb.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        total_number_format = wb.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'
        })
        
        # Tiêu đề báo cáo
        ws.merge_range('A1:S1', "BÁO CÁO XUẤT NHẬP TỒN KHO", title_format)
        
        # Thông tin báo cáo
        ws.write('A3', "Kho:")
        ws.write('B3', report_data.get('location_id', 'N/A'))
        ws.write('A4', "Từ ngày:")
        ws.write('B4', report_data.get('date_from_str', 'N/A'))
        ws.write('A5', "Đến ngày:")
        ws.write('B5', report_data.get('date_to_str', 'N/A'))
        ws.write('A6', "Ngày in:")
        ws.write('B6', report_data.get('current_time', 'N/A'))
        ws.write('A7', "Người xuất báo cáo:")
        ws.write('B7', report_data.get('user_name', 'N/A'))
        
        # Header chính
        row = 9
        ws.merge_range(f'A{row}:D{row}', "STT", header_format)
        ws.write(f'E{row}', "Tên sản phẩm", header_format)
        ws.write(f'F{row}', "Mã sản phẩm", header_format)
        ws.write(f'G{row}', "Đơn vị", header_format)
        ws.write(f'H{row}', "Tồn đầu kỳ", header_format)
        ws.merge_range(f'I{row}:M{row}', "Nhập", header_format)
        ws.merge_range(f'N{row}:R{row}', "Xuất", header_format)
        ws.write(f'S{row}', "Tồn cuối kỳ", header_format)
        
        # Header phụ
        row = 10
        ws.write(f'A{row}', "", sub_header_format)
        ws.write(f'B{row}', "", sub_header_format)
        ws.write(f'C{row}', "", sub_header_format)
        ws.write(f'D{row}', "", sub_header_format)
        ws.write(f'E{row}', "", sub_header_format)
        ws.write(f'F{row}', "", sub_header_format)
        ws.write(f'G{row}', "", sub_header_format)
        ws.write(f'H{row}', "", sub_header_format)
        ws.write(f'I{row}', "Nội bộ", sub_header_format)
        ws.write(f'J{row}', "Điều chỉnh", sub_header_format)
        ws.write(f'K{row}', "Mua", sub_header_format)
        ws.write(f'L{row}', "Trả hàng", sub_header_format)
        ws.write(f'M{row}', "Tổng", sub_header_format)
        ws.write(f'N{row}', "Nội bộ", sub_header_format)
        ws.write(f'O{row}', "Bán", sub_header_format)
        ws.write(f'P{row}', "Điều chỉnh", sub_header_format)
        ws.write(f'Q{row}', "Trả hàng", sub_header_format)
        ws.write(f'R{row}', "Tổng", sub_header_format)
        ws.write(f'S{row}', "", sub_header_format)
        
        # Dữ liệu
        opening_stock = report_data.get('opening_stock', [])
        incoming_stock = report_data.get('incoming_stock', [])
        outgoing_stock = report_data.get('outgoing_stock', [])
        closing_stock = report_data.get('closing_stock', [])
        
        # Tạo dict để dễ truy cập
        opening_dict = {item['product']['id']: item for item in opening_stock}
        incoming_dict = {item['product']['id']: item for item in incoming_stock}
        outgoing_dict = {item['product']['id']: item for item in outgoing_stock}
        closing_dict = {item['product']['id']: item for item in closing_stock}
        
        # Lấy tất cả sản phẩm
        all_product_ids = set(opening_dict.keys()) | set(incoming_dict.keys()) | set(outgoing_dict.keys())
        
        # Sắp xếp theo tên sản phẩm
        def get_product_name(product_id):
            if product_id in opening_dict:
                return opening_dict[product_id]['product']['name']
            elif product_id in incoming_dict:
                return incoming_dict[product_id]['product']['name']
            elif product_id in outgoing_dict:
                return outgoing_dict[product_id]['product']['name']
            return ''
        
        sorted_products = sorted(all_product_ids, key=get_product_name)
        
        row = 11
        for index, product_id in enumerate(sorted_products):
            product = None
            if product_id in opening_dict:
                product = opening_dict[product_id]['product']
            elif product_id in incoming_dict:
                product = incoming_dict[product_id]['product']
            elif product_id in outgoing_dict:
                product = outgoing_dict[product_id]['product']
            
            if not product:
                continue
            
            # STT
            ws.write(f'A{row}', index + 1, center_format)
            
            # Tên sản phẩm
            ws.write(f'E{row}', product.get('name', 'N/A'), text_format)
            
            # Mã sản phẩm
            ws.write(f'F{row}', product.get('default_code', ''), text_format)
            
            # Đơn vị
            uom = (opening_dict.get(product_id, {}).get('uom') or 
                   incoming_dict.get(product_id, {}).get('uom') or 
                   outgoing_dict.get(product_id, {}).get('uom') or 
                   'N/A')
            ws.write(f'G{row}', uom, center_format)
            
            # Tồn đầu kỳ
            opening_qty = opening_dict.get(product_id, {}).get('quantity', 0)
            ws.write(f'H{row}', opening_qty, right_format)
            
            # Nhập nội bộ
            incoming_internal = incoming_dict.get(product_id, {}).get('internal_qty', 0)
            ws.write(f'I{row}', incoming_internal, right_format)
            
            # Nhập mua
            incoming_purchase_po = incoming_dict.get(product_id, {}).get('purchase_qty_po', 0)
            ws.write(f'J{row}', incoming_purchase_po, right_format)
            
            # Nhập điều chỉnh
            incoming_purchase_manual = incoming_dict.get(product_id, {}).get('purchase_qty_manual', 0)
            ws.write(f'K{row}', incoming_purchase_manual, right_format)
            
            # Nhập trả hàng
            incoming_return = incoming_dict.get(product_id, {}).get('return_qty', 0)
            ws.write(f'L{row}', incoming_return, right_format)
            
            # Tổng nhập
            incoming_total = incoming_dict.get(product_id, {}).get('quantity', 0)
            ws.write(f'M{row}', incoming_total, right_format)
            
            # Xuất nội bộ
            outgoing_internal = outgoing_dict.get(product_id, {}).get('internal_qty', 0)
            ws.write(f'N{row}', outgoing_internal, right_format)
            
            # Xuất bán
            outgoing_sale_so = outgoing_dict.get(product_id, {}).get('sale_qty_so', 0)
            ws.write(f'O{row}', outgoing_sale_so, right_format)
            
            # Xuất điều chỉnh
            outgoing_sale_manual = outgoing_dict.get(product_id, {}).get('sale_qty_manual', 0)
            ws.write(f'P{row}', outgoing_sale_manual, right_format)
            
            # Xuất trả hàng
            outgoing_return = outgoing_dict.get(product_id, {}).get('return_qty', 0)
            ws.write(f'Q{row}', outgoing_return, right_format)
            
            # Tổng xuất
            outgoing_total = outgoing_dict.get(product_id, {}).get('quantity', 0)
            ws.write(f'R{row}', outgoing_total, right_format)
            
            # Tồn cuối kỳ
            closing_qty = closing_dict.get(product_id, {}).get('quantity', 0)
            ws.write(f'S{row}', closing_qty, right_format)
            
            row += 1
        
        # Tổng cộng
        ws.merge_range(f'A{row}:D{row}', "TỔNG CỘNG", total_format)
        
        # Tổng tồn đầu
        total_opening = sum(item.get('quantity', 0) for item in opening_stock)
        ws.write(f'H{row}', total_opening, total_number_format)
        
        # Tổng nhập nội bộ
        total_incoming_internal = sum(item.get('internal_qty', 0) for item in incoming_stock)
        ws.write(f'I{row}', total_incoming_internal, total_number_format)
        
        # Tổng nhập mua
        total_incoming_purchase_po = sum(item.get('purchase_qty_po', 0) for item in incoming_stock)
        ws.write(f'J{row}', total_incoming_purchase_po, total_number_format)
        
        # Tổng nhập điều chỉnh
        total_incoming_purchase_manual = sum(item.get('purchase_qty_manual', 0) for item in incoming_stock)
        ws.write(f'K{row}', total_incoming_purchase_manual, total_number_format)
        
        # Tổng nhập trả hàng
        total_incoming_return = sum(item.get('return_qty', 0) for item in incoming_stock)
        ws.write(f'L{row}', total_incoming_return, total_number_format)
        
        # Tổng nhập
        total_incoming = sum(item.get('quantity', 0) for item in incoming_stock)
        ws.write(f'M{row}', total_incoming, total_number_format)
        
        # Tổng xuất nội bộ
        total_outgoing_internal = sum(item.get('internal_qty', 0) for item in outgoing_stock)
        ws.write(f'N{row}', total_outgoing_internal, total_number_format)
        
        # Tổng xuất bán
        total_outgoing_sale_so = sum(item.get('sale_qty_so', 0) for item in outgoing_stock)
        ws.write(f'O{row}', total_outgoing_sale_so, total_number_format)
        
        # Tổng xuất điều chỉnh
        total_outgoing_sale_manual = sum(item.get('sale_qty_manual', 0) for item in outgoing_stock)
        ws.write(f'P{row}', total_outgoing_sale_manual, total_number_format)
        
        # Tổng xuất trả hàng
        total_outgoing_return = sum(item.get('return_qty', 0) for item in outgoing_stock)
        ws.write(f'Q{row}', total_outgoing_return, total_number_format)
        
        # Tổng xuất
        total_outgoing = sum(item.get('quantity', 0) for item in outgoing_stock)
        ws.write(f'R{row}', total_outgoing, total_number_format)
        
        # Tổng tồn cuối
        total_closing = sum(item.get('quantity', 0) for item in closing_stock)
        ws.write(f'S{row}', total_closing, total_number_format)
        
        # Điều chỉnh độ rộng cột
        ws.set_column('A:D', 5)  # STT
        ws.set_column('E:E', 30)  # Tên sản phẩm
        ws.set_column('F:F', 15)  # Mã sản phẩm
        ws.set_column('G:G', 10)  # Đơn vị
        ws.set_column('H:H', 12)  # Tồn đầu kỳ
        ws.set_column('I:M', 12)  # Nhập
        ws.set_column('N:R', 12)  # Xuất
        ws.set_column('S:S', 12)  # Tồn cuối kỳ
        
        # Lưu file
        wb.close()
        excel_data = output.getvalue()
        
        # Tạo attachment
        filename = f"bao_cao_kho_{report_data.get('date_from_str', '')}_{report_data.get('date_to_str', '')}.xlsx"
        
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(excel_data),
            'res_model': 'stock.inventory.report.wizard',
            'res_id': self.id,
        })
        
        # Trả về action để download file
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    def _prepare_report_data(self):
        self.ensure_one()
        
        # Lấy dữ liệu tồn đầu kỳ
        opening_stock = self._get_opening_stock()
        
        # Lấy dữ liệu nhập trong kỳ
        incoming_stock = self._get_incoming_stock()
        
        # Lấy dữ liệu xuất trong kỳ
        outgoing_stock = self._get_outgoing_stock()
        
        # Tính tồn cuối kỳ
        closing_stock = self._calculate_closing_stock(opening_stock, incoming_stock, outgoing_stock)
        
        return {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'date_from_str': fields.Datetime.context_timestamp(self, self.date_from).strftime('%d/%m/%Y %H:%M:%S') if self.date_from else 'N/A',
            'date_to_str': fields.Datetime.context_timestamp(self, self.date_to).strftime('%d/%m/%Y %H:%M:%S') if self.date_to else 'N/A',
            'location_id': self.location_id.display_name,
            'current_time': fields.Datetime.context_timestamp(self, fields.Datetime.now()).strftime('%d/%m/%Y %H:%M:%S'),
            'user_name': self.env.user.name,
            'opening_stock': opening_stock,
            'incoming_stock': incoming_stock,
            'outgoing_stock': outgoing_stock,
            'closing_stock': closing_stock,
        }

    def _get_opening_stock(self):
        self.ensure_one()
        
        # Tính tồn cuối kỳ trước (thời điểm trước date_from)
        previous_date = self.date_from - timedelta(days=1)
        
        # Lấy tất cả sản phẩm có tồn kho
        products = self.env['product.product'].search([
            ('type', '=', 'product')
        ])
        
        # Tính tồn cuối kỳ trước dựa trên stock moves đến ngày previous_date
        opening_data = {}
        
        for product in products:
            # Tính tồn cuối kỳ trước bằng cách lấy tổng moves đến ngày previous_date
            moves_before = self.env['stock.move'].search([
                ('product_id', '=', product.id),
                ('date', '<=', previous_date),
                ('state', '=', 'done')
            ])
            
            # Tính tổng nhập vào kho được chọn
            moves_in = sum(moves_before.filtered(
                lambda m: m.location_dest_id.id == self.location_id.id and 
                m.location_id.usage != 'internal'
            ).mapped('product_uom_qty'))
            
            # Tính tổng xuất từ kho được chọn
            moves_out = sum(moves_before.filtered(
                lambda m: m.location_id.id == self.location_id.id and 
                m.location_dest_id.usage != 'internal'
            ).mapped('product_uom_qty'))
            
            opening_qty = moves_in - moves_out
            
            if moves_in > 0 or moves_out > 0:
                opening_data[product.id] = {
                    'product': { 'name': product.name, 'id': product.id, 'default_code': product.default_code },
                    'quantity': opening_qty,
                    'uom': product.uom_id.name if product.uom_id else 'N/A',
                }
        
        return list(opening_data.values())

    def _get_incoming_stock(self):
        self.ensure_one()
        
        incoming_moves = self.env['stock.move'].search([
            ('location_dest_id.id', '=', self.location_id.id),
            ('location_id.usage', '!=', 'internal'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'done')
        ])
        
        incoming_data = {}
        for move in incoming_moves:
            product = move.product_id
            if product.id not in incoming_data:
                incoming_data[product.id] = {
                    'product': { 'name': product.name, 'id': product.id, 'default_code': product.default_code },
                    'quantity': 0,
                    'uom': product.uom_id.name if product.uom_id else 'N/A',
                    'internal_qty': 0,  # Nhập nội bộ
                    'purchase_qty_po': 0,   # Nhập mua
                    'purchase_qty_manual': 0,   # Nhập điều chỉnh
                    'return_qty': 0,     # Nhập trả hàng
                    'other_qty': 0,     # Nhập khác
                }
            
            picking_type = move.picking_id.picking_type_id.code if move.picking_id and move.picking_id.picking_type_id else ''
            
            if picking_type == 'internal':
                incoming_data[product.id]['internal_qty'] += move.product_uom_qty
            elif picking_type in ['incoming', 'purchase']:
                # Kiểm tra xem có phải từ Purchase Order không (thay vì SO)
                if move.picking_id and move.picking_id.purchase_id:
                    incoming_data[product.id]['purchase_qty_po'] += move.product_uom_qty
                else:
                    incoming_data[product.id]['purchase_qty_manual'] += move.product_uom_qty
            elif picking_type == 'return':
                incoming_data[product.id]['return_qty'] += move.product_uom_qty
            else:
                incoming_data[product.id]['other_qty'] += move.product_uom_qty
            
            incoming_data[product.id]['quantity'] += move.product_uom_qty
        
        return list(incoming_data.values())

    def _get_outgoing_stock(self):
        """Lấy dữ liệu xuất trong kỳ"""
        self.ensure_one()
        
        outgoing_moves = self.env['stock.move'].search([
            ('location_id.id', '=', self.location_id.id),
            ('location_dest_id.usage', '!=', 'internal'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'done')
        ])
        
        outgoing_data = {}
        for move in outgoing_moves:
            product = move.product_id
            if product.id not in outgoing_data:
                outgoing_data[product.id] = {
                    'product': { 'name': product.name, 'id': product.id, 'default_code': product.default_code },
                    'quantity': 0,
                    'uom': product.uom_id.name if product.uom_id else 'N/A',
                    'internal_qty': 0,  
                    'sale_qty_so': 0,     # Xuất bán
                    'sale_qty_manual': 0, # Xuất điều chỉnh
                    'return_qty': 0,   # Xuất trả hàng
                    'other_qty': 0,
                }
            
            picking_type = move.picking_id.picking_type_id.code if move.picking_id and move.picking_id.picking_type_id else ''
            
            if picking_type == 'internal':
                outgoing_data[product.id]['internal_qty'] += move.product_uom_qty
            elif picking_type in ['outgoing', 'delivery']:
                # Kiểm tra xem có phải từ Sale Order không
                if move.picking_id and move.picking_id.sale_id:
                    outgoing_data[product.id]['sale_qty_so'] += move.product_uom_qty
                else:
                    outgoing_data[product.id]['sale_qty_manual'] += move.product_uom_qty
            elif picking_type == 'return':
                outgoing_data[product.id]['return_qty'] += move.product_uom_qty
            else:
                outgoing_data[product.id]['other_qty'] += move.product_uom_qty
            
            outgoing_data[product.id]['quantity'] += move.product_uom_qty
        
        return list(outgoing_data.values())

    def _calculate_closing_stock(self, opening_stock, incoming_stock, outgoing_stock):
        opening_dict = {item['product']['id']: item for item in opening_stock}
        incoming_dict = {item['product']['id']: item for item in incoming_stock}
        outgoing_dict = {item['product']['id']: item for item in outgoing_stock}
        
        all_product_ids = set(opening_dict.keys()) | set(incoming_dict.keys()) | set(outgoing_dict.keys())
        
        closing_data = []
        for product_id in all_product_ids:
            opening_qty = opening_dict.get(product_id, {}).get('quantity', 0)
            incoming_qty = incoming_dict.get(product_id, {}).get('quantity', 0)
            outgoing_qty = outgoing_dict.get(product_id, {}).get('quantity', 0)
            
            closing_qty = opening_qty + incoming_qty - outgoing_qty
            
            product_info = None
            if product_id in opening_dict:
                product_info = opening_dict[product_id]['product']
            elif product_id in incoming_dict:
                product_info = incoming_dict[product_id]['product']
            elif product_id in outgoing_dict:
                product_info = outgoing_dict[product_id]['product']
            
            closing_data.append({
                'product': product_info,
                'quantity': closing_qty,
                'uom': (opening_dict.get(product_id, {}).get('uom') or 
                        incoming_dict.get(product_id, {}).get('uom') or 
                        outgoing_dict.get(product_id, {}).get('uom') or 
                        'N/A'),
            })
        
        return closing_data
