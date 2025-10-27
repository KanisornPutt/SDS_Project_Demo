FROM golang:1.21 AS builder
WORKDIR /app
COPY pdf_service.go .
RUN go build -o pdf_service pdf_service.go

FROM debian:bookworm-slim
RUN apt-get update && \
    apt-get install -y wkhtmltopdf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/pdf_service /app/pdf_service
EXPOSE 8080
CMD ["/app/pdf_service"]