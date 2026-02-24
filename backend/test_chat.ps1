$body = @{
    messages = @(
        @{
            role = "user"
            content = "Hello, what is a car?"
        }
    )
    context = "automotive"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/chat" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing | Select-Object -ExpandProperty Content
