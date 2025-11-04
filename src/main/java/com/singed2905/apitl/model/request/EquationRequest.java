package com.singed2905.apitl.model.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.*;
import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.List;

/**
 * Equation Request - Hệ phương trình tuyến tính
 * 
 * Hỗ trợ hệ 2×2, 3×3, 4×4 với format:
 * - 2×2: [a11, a12, c1, a21, a22, c2] 
 * - 3×3: [a11, a12, a13, c1, a21, a22, a23, c2, a31, a32, a33, c3]
 * - 4×4: [a11, a12, a13, a14, c1, ..., a44, c4]
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Hệ phương trình tuyến tính request")
public class EquationRequest {

    @NotNull
    @Min(value = 2, message = "Số ẩn phải từ 2 trở lên")
    @Max(value = 4, message = "Số ẩn tối đa là 4")
    @Schema(description = "Số ẩn trong hệ phương trình", example = "3", allowableValues = {"2", "3", "4"})
    private Integer variables;

    @NotEmpty
    @Size(min = 6, message = "Hệ 2×2 cần tối thiểu 6 hệ số")
    @Size(max = 20, message = "Hệ 4×4 tối đa 20 hệ số")
    @Schema(description = "Danh sách hệ số phương trình", 
            example = "[\"1\", \"2\", \"3\", \"4\", \"5\", \"6\", \"7\", \"8\", \"9\", \"10\", \"11\", \"12\"]")
    private List<String> coefficients;

    @NotBlank
    @Schema(description = "Phiên bản máy tính Casio", 
            example = "fx799", 
            allowableValues = {"fx799", "fx800", "fx801", "fx802", "fx803"})
    private String calculatorVersion;

    @Schema(description = "Tên bài toán (optional)", example = "Hệ phương trình bài 1")
    private String problemName;

    @Schema(description = "Ghi chú bổ sung", example = "Kiểm tra nghiệm")
    private String notes;

    @Schema(description = "Có sinh keylog hay không", example = "true")
    private Boolean generateKeylog = true;

    @Schema(description = "Có giải hệ phương trình hay không", example = "true") 
    private Boolean solveSolution = true;

    /**
     * Validate số lượng hệ số theo số ẩn
     */
    public boolean isValidCoefficientCount() {
        if (coefficients == null || variables == null) {
            return false;
        }
        
        int expectedCount = switch (variables) {
            case 2 -> 6;  // 2×3 matrix: a11,a12,c1,a21,a22,c2
            case 3 -> 12; // 3×4 matrix: a11,...,a33,c1,c2,c3
            case 4 -> 20; // 4×5 matrix: a11,...,a44,c1,c2,c3,c4
            default -> 0;
        };
        
        return coefficients.size() == expectedCount;
    }
}