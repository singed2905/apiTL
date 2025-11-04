package com.singed2905.apitl;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class ApiTlApplicationTests {

    @Test
    void contextLoads() {
        // Test that Spring context loads successfully
    }

    @Test
    void applicationStartsSuccessfully() {
        // Basic smoke test to ensure application can start
        // More detailed tests will be added in separate test classes
    }
}
