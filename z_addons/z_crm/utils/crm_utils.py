# file này tạo ra một class để chứ hoạt động với các hàm liên quan đến CRM.

class CRMUtils:
    
    @staticmethod
    def create_log(instance, model_name, is_success, log_message):
        instance.env["z.crm.logs"].create({
                        "task_id": instance.id,
                        "model_name": model_name,
                        "retry_time": instance.count_retry,
                        "is_success": is_success,
                        "queue_logs":  log_message,})