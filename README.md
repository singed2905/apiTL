# ConvertKeylogApp API

A Spring Boot REST API for keylog conversion, processing, and analysis.

## Features

- **Keylog Processing**: Upload and process keylog files
- **Format Conversion**: Convert keylogs between JSON, CSV, XML, and TXT formats
- **Advanced Analysis**: Typing statistics, speed analysis, pattern detection
- **Data Management**: Store, retrieve, and manage keylog data
- **REST API**: Comprehensive REST endpoints with Swagger documentation

## Quick Start

### Prerequisites

- Java 11 or higher
- Maven 3.6+
- MySQL (for production) or H2 (for development)

### Running the Application

1. **Clone the repository:**
   ```bash
   git clone https://github.com/singed2905/apiTL.git
   cd apiTL
   ```

2. **Build the application:**
   ```bash
   mvn clean install
   ```

3. **Run with H2 database (development):**
   ```bash
   mvn spring-boot:run
   ```

4. **Run with MySQL (production):**
   ```bash
   mvn spring-boot:run -Dspring.profiles.active=prod
   ```

5. **Access the application:**
   - API Base URL: `http://localhost:8080`
   - Swagger UI: `http://localhost:8080/swagger-ui.html`
   - H2 Console (dev only): `http://localhost:8080/h2-console`

## API Endpoints

### Keylog Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/keylogs/upload` | Upload keylog file |
| GET | `/api/v1/keylogs` | Get all keylogs |
| GET | `/api/v1/keylogs/session/{sessionId}` | Get keylogs by session |
| DELETE | `/api/v1/keylogs/{id}` | Delete keylog |
| GET | `/api/v1/keylogs/stats` | Get overall statistics |
| GET | `/api/v1/keylogs/search` | Search keylogs by pattern |

### Format Conversion

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/convert` | Convert keylog format |
| GET | `/api/v1/convert/formats` | Get supported formats |
| POST | `/api/v1/convert/to-json` | Convert to JSON |
| POST | `/api/v1/convert/to-csv` | Convert to CSV |
| POST | `/api/v1/convert/to-xml` | Convert to XML |
| POST | `/api/v1/convert/batch` | Batch conversion |

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analysis/stats/{sessionId}` | Typing statistics |
| GET | `/api/v1/analysis/frequency/{sessionId}` | Key frequency |
| GET | `/api/v1/analysis/speed/{sessionId}` | Typing speed analysis |
| GET | `/api/v1/analysis/patterns/{sessionId}` | Pattern detection |
| GET | `/api/v1/analysis/dwell-time/{sessionId}` | Dwell time analysis |
| GET | `/api/v1/analysis/flight-time/{sessionId}` | Flight time analysis |
| GET | `/api/v1/analysis/compare` | Compare typing patterns |

## File Format

### Input Keylog Format

The API expects keylog files in CSV format with the following structure:

```
timestamp,keystroke,keytype,duration
2023-11-04T10:30:00,a,letter,150
2023-11-04T10:30:01,b,letter,120
2023-11-04T10:30:02,Space,space,200
```

### Supported Output Formats

- **JSON**: Structured data with metadata
- **CSV**: Comma-separated values
- **XML**: Well-formed XML document
- **TXT**: Human-readable text format

## Configuration

### Database Configuration

**Development (H2):**
```properties
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.username=sa
spring.datasource.password=
```

**Production (MySQL):**
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/keylogdb
spring.datasource.username=your_username
spring.datasource.password=your_password
```

### Environment Variables

- `DATABASE_URL`: MySQL database URL
- `DATABASE_USERNAME`: Database username
- `DATABASE_PASSWORD`: Database password
- `PORT`: Server port (default: 8080)

## Examples

### Upload Keylog File

```bash
curl -X POST http://localhost:8080/api/v1/keylogs/upload \
  -F "file=@keylog.csv"
```

### Convert to JSON

```bash
curl -X POST http://localhost:8080/api/v1/convert/to-json \
  -d "sessionId=your-session-id"
```

### Get Typing Statistics

```bash
curl http://localhost:8080/api/v1/analysis/stats/your-session-id
```

## Development

### Project Structure

```
src/main/java/com/keylog/converter/
├── controller/          # REST controllers
├── model/              # Data models
├── repository/         # Data access layer
├── service/           # Business logic
└── ConvertKeylogApplication.java  # Main application
```

### Building and Testing

```bash
# Build
mvn clean compile

# Run tests
mvn test

# Package
mvn package

# Run
java -jar target/converter-1.0.0.jar
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For support or questions, please open an issue on GitHub.
