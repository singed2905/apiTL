package com.singed2905.apitl.model.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.*;
import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.List;

/**
 * Polynomial Request - Phương trình polynomial
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Polynomial request")
public class PolynomialRequest {

    @NotNull
    @Min(value = 2, message = "Bậc tối thiểu là 2")
    @Max(value = 4, message = "Bậc tối đa là 4")
    @Schema(description = "Bậc của polynomial", example = "2")
    private Integer degree;

    @NotEmpty
    @Schema(description = "Các hệ số polynomial", example = "[\"1\", \"-5\", \"6\"]")
    private List<String> coefficients;

    @NotBlank
    @Schema(description = "Phiên bản máy tính", example = "fx799")
    private String calculatorVersion;

    @Schema(description = "Tên bài toán")
    private String problemName;

    @Schema(description = "Có tạo keylog không", example = "true")
    private Boolean generateKeylog = true;
}