#
# e.g. `check_unset_variables RM_BASE || exit 1`
#

check_unset_variables() {
  local unset_vars=()
  for var_name in "$@"; do
    if [ -z "${!var_name}" ]; then
      unset_vars+=("$var_name")
    fi
  done

  if [ ${#unset_vars[@]} -eq 0 ]; then

    return 0
  else
    echo "Error: the following variables are unset (running $0):"
    for unset_var in "${unset_vars[@]}"; do
      echo "$unset_var"
    done
    return 1
  fi
}