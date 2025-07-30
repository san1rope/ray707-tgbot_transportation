from .start import router as r_start
from .set_language import router as r_set_language
from .create_order import router as r_create_order
from .create_order_steps import router as r_create_order_steps
from .my_orders import router as r_my_orders

routers = [r_start, r_set_language, r_create_order, r_create_order_steps, r_my_orders]
