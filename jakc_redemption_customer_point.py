from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [
    ('draft','New'),
    ('active','Active'),
    ('done','Close'),
    ('expired','Expired'),
    ('req_delete','Request For Delete'),
    ('delete','Deleted')    
]

class rdm_customer_point(osv.osv):
    _name = 'rdm.customer.point'
    _description = 'Redemption Customer Point'
    
    def _get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]
        return self.browse(cr, uid, trans_id, context=context)
    
    def batch_expired_date(self, cr, uid, context=None):
        sql_req = "UPDATE rdm.customer.point SET state='expired' WHERE expired_date=now()"
        cr.execute(sql_req)
        return True

    def get_active_customer_point(self, cr, uid, context=None):
        args = [('state','=','active')]
        ids = self.search(cr, uid, args, context)
        return self.browse(cr, uid, ids, context)
        
    def get_customer_total_point(self, cr, uid, customer_id, context=None):            
        sql_req = """SELECT sum(a.point) as total FROM rdm_customer_point a   
                  WHERE (a.customer_id={0}) 
                  AND a.state='active' AND a.expired_date > now()""".format(str(customer_id))
                          
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_points = sql_res['total']
        else:
            total_points = 0        
        
        return total_points
    
    def get_customer_total_point_usage(self, cr, uid, customer_id, context=None):            
        sql_req = """SELECT sum(a.point) as total FROM rdm_customer_point_detail a  
                  LEFT JOIN rdm_customer_point b 
                  ON a.customer_point_id = b.id 
                  WHERE (b.customer_id={0}) 
                  AND b.state='active' AND b.expired_date > now()""".format(str(customer_id))
                          
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_points = sql_res['total']
        else:
            total_points = 0        
        
        return total_points 
    
    def _get_usage(self, cr, uid, ids, field_name, args, context=None):          
        id = ids[0]
        total_points = self.pool.get('rdm.customer.point.detail').get_point_usage(cr, uid, id, context=context) 
        res = {}
        res[id] = 0   
        return res
    
    
    def add_point(self, cr, uid, values, context=None):
        _logger.info('Start Add Point')
        trans_data = {}
        trans_data.update({'customer_id': values.get('customer_id')})
        trans_data.update({'trans_id': values.get('trans_id')})
        trans_data.update({'trans_type':values.get('trans_type')})
        trans_data.update({'point': values.get('point')})                             
        self.pool.get('rdm.customer.point').create(cr, uid, trans_data, context=context)
        _logger.info('End Add Point')                
                                
    _columns = {
        'customer_id': fields.many2one('rdm.customer','Customer', required=True),
        'trans_id': fields.integer('Transaction ID', readonly=True),                
        'trans_type': fields.selection([('promo','Promotion'),('point','Point'),('adjust','Adjust'),('reference','Reference'),('member','New Member')], 'Transaction Type'),        
        'point': fields.integer('Point #'),
        'usage': fields.function(_get_usage, type="integer", string='Usage'),
        'is_rollback': fields.boolean('Rollback'),        
        'expired_date': fields.date('Expired Date'),
        'customer_point_detail_ids': fields.one2many('rdm.customer.point.detail','customer_point_id','Details'),
        'state': fields.selection(AVAILABLE_STATES,'Status',size=16,readonly=True), 
    }        
    
    _defaults = {
        'point': lambda *a: 0,        
        'is_rollback': lambda *a: False,
        'state': lambda *a: 'active',
    }
rdm_customer_point()

class rdm_customer_point_detail(osv.osv):
    _name = "rdm.customer.point.detail"
    _description = "Redemption Customer Point Detail"
    
    def get_point_usage(self, cr, uid, trans_id, context=None):
        sql_req = """SELECT sum(a.point) as total FROM rdm_customer_point_detail a  
                  WHERE (a.trans_id={0})  
                  AND state='active' """.format(str(trans_id))
                          
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_points = sql_res['total']
        else:
            total_points = 0        
        
        return total_points    
    
    _columns = {
        'customer_point_id': fields.many2one('rdm.customer.point','Customer Point'),
        'trans_id': fields.integer('Transaction ID', readonly=True),
        'reward_trans_id': fields.integer('Reward Transaction ID', readonly=True),
        'trans_type': fields.selection([('reward','Reward'),('adjust','Adjust')], 'Transaction Type'),                
        'point': fields.integer('Point'),
        'state': fields.selection(AVAILABLE_STATES,'Status',size=16,readonly=True),
    }        
    
rdm_customer_point_detail()