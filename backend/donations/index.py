import json
import os
import psycopg2
from datetime import datetime

def handler(event: dict, context) -> dict:
    '''API для приёма донатов и получения списка благодарностей'''
    
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    
    try:
        if method == 'POST':
            body = json.loads(event.get('body', '{}'))
            donor_name = body.get('donor_name', 'Аноним')
            amount = body.get('amount', 40.0)
            message = body.get('message', '')
            card_type = body.get('card_type', 'Мир')
            
            cur.execute(
                "INSERT INTO donations (donor_name, amount, message, card_type) VALUES (%s, %s, %s, %s) RETURNING id",
                (donor_name, amount, message, card_type)
            )
            donation_id = cur.fetchone()[0]
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'donation_id': donation_id,
                    'message': 'Спасибо за поддержку!'
                })
            }
        
        elif method == 'GET':
            cur.execute(
                "SELECT donor_name, amount, message, card_type, created_at FROM donations ORDER BY created_at DESC LIMIT 50"
            )
            rows = cur.fetchall()
            
            donations = []
            for row in rows:
                donations.append({
                    'donor_name': row[0],
                    'amount': float(row[1]),
                    'message': row[2],
                    'card_type': row[3],
                    'created_at': row[4].isoformat() if row[4] else None
                })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'donations': donations})
            }
        
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    finally:
        cur.close()
        conn.close()
