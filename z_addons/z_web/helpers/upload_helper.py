from odoo import http
from odoo.http import request, Response
import boto3
import requests
 
class S3ImageDownloadController(http.Controller):
 
    @http.route('/get-image', type='http', auth='public', methods=['GET'], csrf=False)
    def download_image(self, **kwargs):
        object_key = kwargs.get('key').replace(" ","")
        if not object_key:
            return Response("Missing image key", status=400)
        access_key =  request.env['ir.config_parameter'].get_param(
            'amazon_s3_connector.amazon_access_key')
        access_secret =  request.env['ir.config_parameter'].get_param(
            'amazon_s3_connector.amazon_secret_key')
        bucket_name =  request.env['ir.config_parameter'].get_param(
            'amazon_s3_connector.amazon_bucket_name')
 
        # Initialize boto3 session
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=access_secret,
        )
        s3_client = session.client('s3')
        try:
            response = s3_client.get_object(
                Bucket=bucket_name,
                Key=object_key
            )
            img_content = response['Body'].read()
            return Response(
                img_content,
                content_type=response.get("ContentType"),
                headers={
                    'Content-Disposition': 'inline'
                }
            )
        except Exception as e:
            print('Failed to Upload Files ( %s .)' % e) 
