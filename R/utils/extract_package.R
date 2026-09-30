#' @title Extract the metadata of all functions of a package
#' @description Shallow-clones the package repository and extracts the
#'   configured fields from every R file in its `R/` folder. It also checks
#'   whether a test file in `tests/testthat` mentions the function name.
#' @param name Package name as given in the package list, used for messages
#'   and the clone folder.
#' @param github_link URL of the package's GitHub repository.
#' @param fields Named list of field definitions from
#'   `config/metadata_fields.yml`.
#' @return Tibble with one row per R file: `file`, `package`,
#'   `function_name`, `test_file` and one column per field. `NULL` if the
#'   repository cannot be cloned.
#' @author Florian Schwarz

extract_package <- function(name, github_link, fields) {
  message("Extracting ", name)
  repo <- file.path(tempdir(), name)
  if (system2("git", c("clone", "--quiet", "--depth", "1", github_link, repo)) != 0) {
    warning("Could not clone ", github_link, ", skipping ", name)
    return(NULL)
  }
  test_files <- list.files(file.path(repo, "tests", "testthat")) |> stringr::str_c(collapse = ", ")

  package_functions <- dplyr::tibble(file = list.files(file.path(repo, "R"), pattern = "\\.[Rr]$", full.names = TRUE)) |>
    dplyr::mutate(package = read.dcf(file.path(repo, "DESCRIPTION"), fields = "Package")[1, 1],
                  function_name = stringr::str_remove(basename(file), "\\.[Rr]$"),
                  test_file = stringr::str_detect(test_files, stringr::fixed(function_name)),
                  metadata = purrr::map(file, extract_fields, fields = fields)) |>
    tidyr::unnest_wider(metadata)

  return(package_functions)
}
