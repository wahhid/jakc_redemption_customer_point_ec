from openerp.osv import fields, osv
import logging
from datetime import datetime

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
                                            
    def trans_close(self, cr, uid, ids, context=None):
        id = ids[0]
        return self.write(cr,uid,id,{'state': 'done'},context=context)
    
    def trans_expired(self, cr, uid, ids, context=None):
        id = ids[0]
        return self.write(cr,uid,id,{'state': 'expired'},context=context)
    
    def process_expired(self, cr, uid, context=None):
        _logger.info('Start Customer Point Process Expired')
        now = datetime.now().strftime('%Y-%m-%d')
        sql_req = "UPDATE rdm_customer_point SET state='expired' WHERE expired_date < '" + now + "' AND state='active'" 
        cr.execute(sql_req)
        _logger.info('End Customer Point Process Expired')
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
    
    def get_usages(self, cr, uid, ids, field_name, arg, context=None):          
        trans_id = ids[0]        
        res = {}
        total_points = self.pool.get('rdm.customer.point.detail').get_point_usages(cr, uid, trans_id, context=context)
        _logger.info('Total Points : ' + str(total_points))                
        res[trans_id] = total_points                
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
                                
    def deduct_point(self, cr, uid, trans_id, customer_id, point, context=None):
        status = False
        total_point = 0
        sisa_point = point        
        today = datetime.today()
        args = [('customer_id','=',customer_id),('expired_date','>', today),('state','=','active')]        
        ids = self.search(cr, uid, args, order='expired_date asc, id desc', context=context)
        point_ids = self.browse(cr, uid, ids, context=context)
                
        for point_id in point_ids:
            avai_point = point_id.point - point_id.usage
            if avai_point < sisa_point:
                total_point = total_point + avai_point             
                sisa_point = sisa_point - total_point   
                trans_data = {}
                trans_data.update({'customer_point_id':point_id.id})
                trans_data.update({'trans_id':trans_id})
                trans_data.update({'trans_type':'reward'})
                trans_data.update({'point':point})                        
                self.pool.get('rdm.customer.point.detail').deduct_point(cr, uid, trans_data, context=context)
                #self.write(cr,uid,[id],{'usage': point_id.usage + avai_point,'state':'done'},context=context)               
                super(rdm_customer_point,self).write(cr, uid, [point_id.id], {'usage': point_id.usage + avai_point}, context=context)             
                self.trans_close(cr, uid, [point_id.id], context)                            
            else:
                total_point = total_point + sisa_point
                trans_data = {}
                trans_data.update({'customer_point_id':point_id.id})
                trans_data.update({'trans_id':trans_id})
                trans_data.update({'trans_type':'reward'})
                trans_data.update({'point':point})                
                self.pool.get('rdm.customer.point.detail').deduct_point(cr, uid, trans_data, context=context)
                #self.write(cr,uid,[id],{'usage': point_id.usage + sisa_point},context=context)  
                super(rdm_customer_point,self).write(cr, uid, [point_id.id], {'usage': point_id.usage + sisa_point}, context=context)                          
                break                       
        
    _columns = {
        'customer_id': fields.many2one('rdm.customer','Customer', required=True),
        'trans_id': fields.integer('Transaction ID', readonly=True),                
        'trans_type': fields.selection([('promo','Promotion'),('point','Point'),('adjust','Adjust'),('reference','Reference'),('member','New Member')], 'Transaction Type'),        
        'point': fields.integer('Point #'),
        #'usage': fields.function(get_usages, type="integer", method=True, string='Usage'),
        'usage': fields.integer('Usage'),      
        'expired_date': fields.date('Expired Date'),
        'customer_point_detail_ids': fields.one2many('rdm.customer.point.detail','customer_point_id','Details'),
        'state': fields.selection(AVAILABLE_STATES,'Status',size=16,readonly=True), 
    }        
    
    _defaults = {
        'point': lambda *a: 0,                
        'state': lambda *a: 'active',
    }
    
rdm_customer_point()

class rdm_customer_point_detail(osv.osv):
    _name = "rdm.customer.point.detail"
    _description = "Redemption Customer Point Detail"
        
    def get_point_usage(self, cr, uid, trans_id, context=None):
        sql_req = """SELECT sum(a.point) as total FROM rdm_customer_point_detail a  
                  WHERE (a.trans_id={0})""".format(str(trans_id))
                          
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_points = sql_res['total']
        else:
            total_points = 0    
                
        if total_points is None:
            total_points = 0
            
        return total_points    

                                       
    def deduct_point(self, cr, uid, values, context=None):
        trans_data = {}
        trans_data.update({'customer_point_id':values.get('customer_point_id')})
        trans_data.update({'trans_id':values.get('trans_id')})
        trans_data.update({'trans_type':values.get('trans_type')})
        trans_data.update({'point':values.get('point')})
        self.create(cr, uid, trans_data, context=context)
    
    _columns = {
        'customer_point_id': fields.many2one('rdm.customer.point','Customer Point'),
        'trans_id': fields.integer('Transaction ID', readonly=True),        
        'trans_type': fields.selection([('reward','Reward'),('adjust','Adjust')], 'Transaction Type'),                
        'point': fields.integer('Point'),        
    }        
    
rdm_customer_point_detail()