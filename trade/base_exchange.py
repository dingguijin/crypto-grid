
from decimal import Decimal, getcontext

class BaseExchange():
    def get_float_precision(self, value):
        # 将 float 转换为 Decimal 对象
        dec_value = Decimal(str(value))
        # 获取小数位数
        precision = abs(dec_value.as_tuple().exponent)
        return precision

    def convert_to_precision(self, value, target_precision):
        # 设置全局精度
        # getcontext().prec = target_precision
        # 将浮点数转换为 Decimal 对象并四舍五入到指定精度
        return float(Decimal(value).quantize(Decimal('1.' + '0' * target_precision)))
