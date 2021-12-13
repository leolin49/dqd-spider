SQL_CREATE_RANK = "CREATE TABLE IF NOT EXISTS {tb} (" \
                  "rank_num INT," \
                  "team VARCHAR(50)," \
                  "game_num INT," \
                  "win INT," \
                  "draw INT," \
                  "lose INT," \
                  "win_goal INT," \
                  "lose_goal INT," \
                  "diff_goal INT," \
                  "score INT" \
                  ")"

SQL_CREATE_TEAM = "CREATE TABLE IF NOT EXISTS {tb} (" \
                  "id INT," \
                  "ch_name VARCHAR(50)," \
                  "en_name VARCHAR(50)," \
                  "country VARCHAR(50)," \
                  "city VARCHAR(50)," \
                  "stadium VARCHAR(50)," \
                  "max_fans INT," \
                  "birth_year INT," \
                  "address VARCHAR(50)" \
                  ")"

SQL_CREATE_PLAYER = "CREATE TABLE IF NOT EXISTS {tb} (" \
                      "id INT," \
                      "ch_name VARCHAR(25)," \
                      "en_name VARCHAR(25)," \
                      "club VARCHAR(25)," \
                      "nation VARCHAR(25)," \
                      "position VARCHAR(25)," \
                      "age INT," \
                      "birthday DATE," \
                      "number INT," \
                      "weight INT," \
                      "height INT" \
                      ")"
