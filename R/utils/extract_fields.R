#' @title Extract all configured fields from an R file
#' @description Reads one R file and applies every field from the config to it.
#'   Fields with `extract: flag` return whether the pattern occurs anywhere in
#'   the file, fields with `extract: value` return the text of the tag.
#' @param file Path to the R file.
#' @param fields Named list of field definitions from
#'   `config/metadata_fields.yml`, each with `pattern` and `extract`.
#' @return Named list with one element per field: `TRUE`/`FALSE` for flag
#'   fields, a string for value fields.
#' @author Florian Schwarz

extract_fields <- function(file, fields) {
  lines <- readLines(file, warn = FALSE)
  values <- purrr::map(fields, \(f) switch(f$extract,
                                           flag = any(stringr::str_detect(lines, f$pattern)),
                                           value = extract_value(lines, f$pattern)))

  return(values)
}
