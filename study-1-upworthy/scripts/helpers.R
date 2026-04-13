# Helper function to format numbers with optional leading zero removal
format_num <- function(x, digits, leading_zero = FALSE) {
  # Ensure x is numeric
  x <- as.numeric(x)
  formatted <- formatC(x, format = "f", digits = digits)
  if (!leading_zero) {
    # Remove leading zero for values between -1 and 1
    formatted <- gsub("^0\\.", ".", formatted)
    formatted <- gsub("^-0\\.", "-.", formatted)
  }
  return(formatted)
}

#' Report fixest model statistics in formatted style
#'
#' @param model A fixest model object (e.g., from feglm)
#' @param variable Name of the variable to report (as character string)
#' @param coef_name Symbol/name for coefficient (default: "β"). Use NULL or FALSE to skip reporting coefficient
#' @param conf_level Confidence level (default: 0.99 for 99%)
#' @param report_pvalue Logical, whether to report p-value (default: TRUE)
#' @param leading_zero Logical, whether to include leading zeros (default: FALSE)
#' @param digits_coef Digits for coefficient and CI (default: 3)
#' @param digits_se Digits for standard error (default: 3)
#' @param digits_stat Digits for test statistic (default: 3)
#' @param p_threshold P-value threshold for "< " notation (default: 0.001)
#' @param scale a scaling factor, e.g., to transform percentages
#'
#' @return A formatted string with the statistics
#'
#' @examples
#' # report_stats(toxicity_fe_1, "toxicity")
#' # report_stats(toxicity_fe_2, "toxicity", coef_name = "b")
#' # report_stats(toxicity_fe_3, "gpt4o_negemo", coef_name = NULL)  # No coefficient
#' # report_stats(toxicity_fe_4, "profanity", coef_name = FALSE)  # No coefficient

report_stats <- function(model, 
                         variable,
                         coef_name = "b",
                         conf_level = 0.99,
                         report_pvalue = FALSE,
                         leading_zero = FALSE,
                         digits_coef = 3,
                         digits_se = 3,
                         digits_stat = 3,
                         p_threshold = 0.001,
                         scale = 1) {
  
  # Check if coefficient should be reported
  report_coef <- !is.null(coef_name) && coef_name != FALSE
  
  # Extract coefficient (ensure it's numeric)
  coef_val <- as.numeric(coef(model)[[variable]]) * scale
  
  # Extract standard error (ensure it's numeric)
  se_val <- as.numeric(se(model)[[variable]]) * scale
  
  # Calculate z-statistic (for GLM models)
  z_val <- coef_val / se_val
  
  # Extract p-value (ensure it's numeric)
  p_val <- as.numeric(pvalue(model)[[variable]])
  
  # Calculate confidence intervals
  # Try multiple methods to get CI
  ci_lower <- NA
  ci_upper <- NA
  
  # Method 1: Try using confint
  tryCatch({
    ci <- confint(model, level = conf_level)
    if (is.matrix(ci)) {
      # Check if variable is in rownames
      if (variable %in% rownames(ci)) {
        ci_lower <- as.numeric(ci[variable, 1]) * scale
        ci_upper <- as.numeric(ci[variable, 2]) * scale
      }
    } else if (is.data.frame(ci)) {
      if (variable %in% rownames(ci)) {
        ci_lower <- as.numeric(ci[variable, 1]) * scale
        ci_upper <- as.numeric(ci[variable, 2]) * scale
      }
    }
  }, error = function(e) {
    # Silent catch
  })
  
  # Method 2: If confint didn't work or returned NA, calculate manually
  if (is.na(ci_lower) || is.na(ci_upper)) {
    z_crit <- qnorm((1 + conf_level) / 2)
    ci_lower <- (coef_val - z_crit * se_val) * scale
    ci_upper <- (coef_val + z_crit * se_val) * scale
  }
  
  # Format the output
  output <- "("
  
  # Add coefficient if requested
  if (report_coef) {
    output <- paste0(
      output,
      coef_name, " = ", 
      format_num(coef_val, digits_coef, leading_zero),
      ", "
    )
  }
  
  # Add SE and z-statistic
  output <- paste0(
    output,
    "SE = ", 
    format_num(se_val, digits_se, leading_zero),
    ", *z* = ", 
    format_num(z_val, digits_stat, leading_zero)
  )
  
  # Add p-value if requested
  if (report_pvalue) {
    if (p_val < p_threshold) {
      output <- paste0(output, ", *P* < ", format_num(p_threshold, 3, leading_zero))
    } else {
      output <- paste0(output, ", *P* = ", 
                       format_num(p_val, 3, leading_zero))
    }
  }
  
  # Add confidence interval
  ci_percent <- conf_level * 100
  output <- paste0(
    output,
    ", ", ci_percent, "% CI = [",
    format_num(ci_lower, digits_coef, leading_zero),
    ", ",
    format_num(ci_upper, digits_coef, leading_zero),
    "])"
  )
  
  return(output)
}

#' Report multiple variables from a model at once
#'
#' @param model A fixest model object
#' @param variables Character vector of variable names (NULL for all)
#' @param ... Additional arguments passed to report_stats
#'
#' @return Named character vector of formatted statistics
report_all_stats <- function(model, variables = NULL, ...) {
  
  # If no variables specified, get all non-intercept coefficients
  if (is.null(variables)) {
    variables <- names(coef(model))
    # Remove intercept if present
    variables <- variables[!variables %in% c("(Intercept)")]
  }
  
  # Apply report_stats to each variable
  results <- sapply(variables, function(var) {
    report_stats(model, var, ...)
  })
  
  return(results)
}

#' Create a comparison table for multiple models
#'
#' @param models List of fixest models
#' @param variable Variable to compare across models
#' @param model_names Names for the models (optional)
#' @param ... Additional arguments passed to report_stats
#'
#' @return A data frame with formatted statistics
compare_models <- function(models, variable, model_names = NULL, ...) {
  
  if (is.null(model_names)) {
    model_names <- paste("Model", seq_along(models))
  }
  
  stats <- sapply(models, function(m) {
    if (variable %in% names(coef(m))) {
      report_stats(m, variable, ...)
    } else {
      NA
    }
  })
  
  df <- data.frame(
    Model = model_names,
    Statistics = stats,
    stringsAsFactors = FALSE
  )
  
  return(df)
}

# Example usage:
# report_stats(toxicity_fe_1, "toxicity")
# # Output: (β = -.009, SE = .001, *z* = -7.664, *P* < .001, 99% CI = (-.012, -.006))
#
# report_stats(toxicity_fe_2, "toxicity", coef_name = "b", conf_level = 0.95)
# # Output: (b = -.009, SE = .001, *z* = -7.664, *P* < .001, 95% CI = (-.011, -.007))
#
# report_stats(toxicity_fe_3, "gpt4o_negemo", coef_name = NULL)
# # Output: (SE = .001, *z* = -7.664, *P* < .001, 99% CI = (-.012, -.006))
#
# report_stats(toxicity_fe_4, "profanity", coef_name = FALSE, report_pvalue = FALSE)
# # Output: (SE = .001, *z* = -7.664, 99% CI = (-.012, -.006))
#
# report_stats(toxicity_fe_4, "profanity", leading_zero = TRUE)  # Use leading zeros
# # Output: (β = -0.009, SE = 0.001, *z* = -7.664, *P* < 0.001, 99% CI = (-0.012, -0.006))
# 
# # Report all coefficients from a model
# report_all_stats(toxicity_fe_4)
# report_all_stats(toxicity_fe_4, leading_zero = TRUE)
# report_all_stats(toxicity_fe_4, coef_name = NULL)  # Without coefficients
# 
# # Compare toxicity across all models
# models_list <- list(toxicity_fe_1, toxicity_fe_2, toxicity_fe_3, toxicity_fe_4)
# compare_models(models_list, "toxicity", 
#                model_names = c("Base", "+Controls", "+Emotion", "+Profanity"))

# Additional helper function to get model info
get_model_info <- function(model) {
  info <- list(
    n_obs = nobs(model),
    n_fe = model$nfixef,
    family = model$family,
    link = model$link
  )
  
  cat("Model Information:\n")
  cat("  Observations:", info$n_obs, "\n")
  cat("  Fixed Effects:", info$n_fe, "\n")
  cat("  Family:", info$family, "\n")
  cat("  Link:", info$link, "\n")
}

# Example: get_model_info(toxicity_fe_1)