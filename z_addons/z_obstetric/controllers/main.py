from odoo import http
from odoo.http import request
import werkzeug


class PrintController(http.Controller):
    @http.route("/print-pdf", type="http", auth="public")
    def print_pdf(self, **kw):
        # Get the PDF URL from the query parameters
        pdf_url = kw.get("url", "")

        # Generate HTML response with JavaScript for auto-printing and closing
        html = f"""
            <html>
            <head>
                <script type="text/javascript">
                    window.onload = function() {{
                        // Open the PDF in a new window
                        var w = window.open('{pdf_url}', '_blank');
                        // Ensure the print dialog is triggered only once
                        w.onload = function() {{
                            w.print();
                            // Close the window after printing
                            w.onafterprint = function() {{
                                w.close();
                            }};
                        window.close();
                            
                        }};
                    }};
                </script>
            </head>
            <body>
                <p>Tập tin của bạn sẽ tự động in. Nếu không, vui lòng kiểm tra cài đặt trình duyệt của bạn.</p>
                </body>
            </html>
            """

        return html

    @http.route(
        [
            "/web/quanlyketquacls",
        ],
        type="http",
        auth="none",
        sitemap=False,
    )
    def generate_url(self, epi_id=False, secret_key="", **kw):
        action = request.env.ref("z_obstetric.z_visit_url_action")
        url = f"/web#action={action.id}&model='z_appointment.appointment'"
        return werkzeug.utils.redirect(url)
