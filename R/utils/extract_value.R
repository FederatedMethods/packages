#' @title Extract the value of a roxygen tag
#' @description Returns the text after the first match of `pattern`, including
#'   the following roxygen lines up to the next tag or the end of the block.
#' @param lines Character vector with the lines of an R file.
#' @param pattern Regular expression matching the tag.
#' @return The extracted text as a single string, or `""` if there is no match.
#' @author Florian Schwarz

extract_value <- function(lines, pattern) {
  pattern_roxygen <- "^\\s*#'"
  pattern_any_tag <- "^\\s*#'\\s*@"

  start <- stringr::str_which(lines, pattern)[1]
  if (is.na(start)) return("")

  following <- lines[-seq_len(start)]
  block_end <- which(!stringr::str_detect(following, pattern_roxygen) |
                       stringr::str_detect(following, pattern_any_tag))[1]
  continuation <- head(following, dplyr::coalesce(block_end - 1L, length(following)))

  value <- c(stringr::str_remove(lines[start], pattern), stringr::str_remove(continuation, pattern_roxygen)) |>
    stringr::str_c(collapse = " ") |>
    stringr::str_squish()

  return(value)
}
