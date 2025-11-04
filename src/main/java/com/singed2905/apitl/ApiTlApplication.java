package com.singed2905.apitl;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * ConvertKeylogApp API - Spring Boot Application
 * 
 * RESTful API for converting mathematical expressions to Casio calculator keylog format.
 * Supports Equation Mode, Polynomial Mode, Geometry Mode, and Vector operations.
 * 
 * Based on ConvertKeylogApp v2.2 Python desktop application.
 * 
 * @author singed2905
 * @version 2.2.0
 */
@SpringBootApplication
public class ApiTlApplication {

    public static void main(String[] args) {
        SpringApplication.run(ApiTlApplication.class, args);
        
        System.out.println("=".repeat(60));
        System.out.println("🚀 ConvertKeylogApp API v2.2.0 Started Successfully!");
        System.out.println("📖 API Documentation: http://localhost:8080/swagger-ui.html");
        System.out.println("🔧 Health Check: http://localhost:8080/actuator/health");
        System.out.println("📊 Metrics: http://localhost:8080/actuator/metrics");
        System.out.println("=".repeat(60));
    }
}