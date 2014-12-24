from openerp.osv import fields, osv

class rdm_customer(osv.osv):    
    _inherit = "rdm.customer"
    
    def get_points(self, cr, uid, ids, field_name, args, context=None):
        id = ids[0]
        res = {}
        #total_usage = self.pool.get('rdm.customer.point').get_customer_total_point_usage(cr, uid, id, context=context)
        #total_point = self.pool.get('rdm.customer.point').get_customer_total_point(cr, uid, id, context=context)                        
        res[id] = 0        
        return res
                            
    _columns = {
        'point': fields.function(get_points, type="integer", string='Points'),
        'customer_point_ids': fields.one2many('rdm.customer.point','customer_id','Points',readonly=True)        
    }
            
rdm_customer()