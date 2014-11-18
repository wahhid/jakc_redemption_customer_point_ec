from openerp.osv import fields, osv

class rdm_customer(osv.osv):    
    _inherit = "rdm.customer"
    
    def get_points(self, cr, uid, ids, field_name, args, context=None):
        id = ids[0]
        res = {}
        sql_req= "SELECT sum(c.point) as total FROM rdm_customer_point c WHERE (c.customer_id=" + str(id) + ") AND state='active' AND expired_date > now()"        
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_coupons = sql_res['total']
        else:
            total_coupons = 0        
        res[id] = total_coupons    
        return res
                    
    _columns = {
        'point': fields.function(get_points, type="integer", string='Points'),
        'customer_point_ids': fields.one2many('rdm.customer.point','customer_id','Points',readonly=True)        
    }
rdm_customer()