from openerp.osv import fields, osv

AVAILABLE_STATES = [
    ('draft','New'),
    ('active','Active'),
    ('expired','Expired'),
    ('req_delete','Request For Delete'),
    ('delete','Deleted')    
]

class rdm_customer_point(osv.osv):
    _name = 'rdm.customer.point'
    _description = 'Redemption Customer Point'
    
    def batch_expired_date(self, cr, uid, context=None):
        sql_req = "UPDATE rdm.customer.point SET state='expired' WHERE expired_date=now()"
        cr.execute(sql_req)
        return True
        
    _columns = {
        'customer_id': fields.many2one('rdm.customer','Customer', required=True),
        'trans_id': fields.integer('Transaction ID', readonly=True),
        'reward_trans_id': fields.integer('Reward Transaction ID', readonly=True),
        'trans_type': fields.selection([('promo','Promotion'),('point','Point'),('reward','Reward'),('adjust','Adjust'),('reference','Reference'),('member','New Member')], 'Transaction Type'),        
        'point': fields.integer('Point #'),
        'expired_date': fields.date('Expired Date'),
        'state': fields.selection(AVAILABLE_STATES,'Status',size=16,readonly=True), 
    }        
    
    _defaults = {
        'state': lambda *a: 'active',
    }
rdm_customer_point()
