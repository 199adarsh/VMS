def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Hello from Vercel!</h1><p>This is a test deployment.</p>'
    }
