# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anfas Faisal K (odoo@cybrosys.info)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import boto3
import mimetypes
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.z_web.helpers.utils import ZUtils

class AmazonUploadFile(models.TransientModel):
    """
    For opening wizard view
    """
    _name = "amazon.upload.file"
    _description = "Amazon Upload File"

    file = fields.Binary(string="Attachment", help="Select a file to upload")
    file_name = fields.Char(string="File Name",
                            help="Name of the file to upload")
    record_id = fields.Integer(string="Record ID", help="ID of the record to update")
    folder_path = fields.Text()

    def action_amazon_upload(self):
        """
        Uploads file to Amazon S3
        """
        attachment = self.env["ir.attachment"].search(
            ['|', ('res_field', '!=', False), ('res_field', '=', False),
             ('res_id', '=', self.id),
             ('res_model', '=', 'amazon.upload.file')])
        if not attachment:
            raise ValidationError(
                'Failed to Upload File')
        
        try:
            medical_test_record = self.env['z_obstetric.medical_test_line'].browse(self.record_id)
            if not medical_test_record: 
                raise ValueError('Record not found.')

            client = boto3.resource(
                's3',
                aws_access_key_id=self.env['ir.config_parameter'].get_param(
                    'amazon_s3_connector.amazon_access_key'),
                aws_secret_access_key=self.env[
                    'ir.config_parameter'].get_param(
                    'amazon_s3_connector.amazon_secret_key'))
            key_name = f'{self.file_name.replace(" ","")}'
            
            client.Bucket(self.env['ir.config_parameter'].get_param(
                'amazon_s3_connector.amazon_bucket_name')).put_object(
                Key= key_name,
                Body=open(attachment._full_path(attachment.store_fname),
                          'rb'),
                ContentDisposition='inline',
                ContentType= attachment.mimetype
                )
            medical_test_record.write({"result_image_url": key_name})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': _('File has been uploaded successfully. Please refresh the page.'),
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        except Exception as e:
            raise ValidationError(
                'Failed to Upload Files ( %s .)' % e)
