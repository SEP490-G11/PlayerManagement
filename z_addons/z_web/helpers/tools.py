class ZTools:
    @staticmethod
    def async_exec(instance, func, *args):
        try:
            new_cr = instance.pool.cursor()
            self = instance.with_env(instance.env(cr=new_cr))
            func(self, *args)
            new_cr.commit()
        except Exception as e:
            print("Exception: ", e)
