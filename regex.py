REGEX_TEST =    ''

REGEX_PERSON = '<div class="player-info" data-v-.*?>' \
               '<div class="info-left" data-v-.*?>' \
               '<p class="china-name" data-v-.*?>(.*?)<img .*? data-v-.*?></p> ' \
               '<p class="en-name" data-v-.*?>(.*?)</p> ' \
               '<div class="detail-info" data-v-.*?>' \
               '<ul data-v-.*?>' \
               '<li data-v-.*?><span data-v-.*?>俱乐部：</span>(.*?)</li> ' \
               '<li data-v-.*?><span data-v-.*?>国   籍：</span>(.*?)</li> ' \
               '<li data-v-.*?><span data-v-.*?>身   高：</span>(.*?)CM</li>' \
               '</ul> ' \
               '<ul class="second-ul" data-v-.*?>' \
               '<li data-v-.*?><span data-v-.*?>位   置：</span>(.*?)</li> ' \
               '<li data-v-.*?><span data-v-.*?>年   龄：</span>(.*?)岁</li> ' \
               '<li data-v-.*?><span data-v-.*?>体   重：</span>(.*?)KG</li>' \
               '</ul> ' \
               '<ul data-v-.*?>' \
               '<li data-v-.*?><span data-v-.*?>号   码：</span>(.*?)号</li> ' \
               '<li data-v-.*?><span data-v-.*?>生   日：</span>(.*?)</li> ' \
               '<li data-v-.*?><span data-v-.*?>惯用脚：</span>(.*?)</li>' \
               '</ul>' \
               '</div>' \
               '</div> ' \
               '<img src="(.*?)" alt class="player-photo" data-v-.*?>' \
               '</div>'

REGEX_TEAM = '<div class="team-info" data-v-.*?>' \
             '<img src="(.*?)" alt class="team-logo" data-v-.*?> ' \
             '<div class="info-con" data-v-.*?>' \
             '<p class="team-name" data-v-.*?>(.*?)<img src=.*? alt data-v-.*?></p> ' \
             '<p class="en-name" data-v-.*?>(.*?)</p> ' \
             '<p data-v-.*?>' \
             '<span class="wid\d+" data-v-.*?><b data-v-.*?>成   立：</b>(.*?)</span>' \
             '<span class="wid\d+" data-v-.*?><b data-v-.*?>国   家：</b>(.*?)</span>' \
             '<span class="wid\d+" data-v-.*?><b data-v-.*?>城   市：</b>(.*?)</span>' \
             '</p> ' \
             '<p data-v-.*?>' \
             '<span class="wid\d+" data-v-.*?><b data-v-.*?>主   场：</b>(.*?)</span>' \
             '<span class="wid\d+" data-v-.*?><b data-v-.*?>容   纳：</b>(.*?)人</span>' \
             '</p> ' \
             '<p data-v-.*?>' \
             '<span class="wid\d+" data-v-.*?><b data-v-.*?>电   话：</b>(.*?)</span>' \
             '<span class="wid\d+" data-v-.*?><b data-v-.*?>邮   箱：</b>(.*?)</span>' \
             '</p> ' \
             '<p class="address" data-v-.*?><b data-v-.*?>地   址：</b>(.*?)' \
             '</p>' \
             '</div>' \
             '</div>'

REGEX_RANK = '<div class="team_point_ranking" data-v-.*?>' \
             '<div data-v-.*?>' \
             '<div data-v-.*?>' \
             '<div class="group-title" data-v-.*?>联赛</div>\s*' \
             '<p class="th" data-v-.*?>'\
             '<span data-v-.*?>排名</span>'\
             '<span data-v-.*?>球队</span>'\
             '<span data-v-.*?>场次</span>'\
             '<span data-v-.*?>胜</span>'\
             '<span data-v-.*?>平</span>'\
             '<span data-v-.*?>负</span>'\
             '<span data-v-.*?>进球</span>'\
             '<span data-v-.*?>失球</span>'\
             '<span data-v-.*?>净胜球</span>'\
             '<span data-v-.*?>积分</span>'\
             '</p>\s*'\
             '<div data-v-.*?>(.*?)</div>'\
             '</div>'\
             '</div>'\
             '</div>'


REGEX_RANK_TEAM = '<p class="td" data-v-522af60a>'\
                  '<span data-v-522af60a>{rank}</span>'\
                  '<span class="team-icon" data-v-522af60a>'\
                  '<img src=".*?" alt data-v-522af60a>'\
                  '<b data-v-522af60a>(.*?)</b></span>'\
                  '<span data-v-522af60a>(.*?)</span>'\
                  '<span data-v-522af60a>(.*?)</span>'\
                  '<span data-v-522af60a>(.*?)</span>'\
                  '<span data-v-522af60a>(.*?)</span>'\
                  '<span data-v-522af60a>(.*?)</span>'\
                  '<span data-v-522af60a>(.*?)</span>'\
                  '<span data-v-522af60a>(.*?)</span>'\
                  '<span data-v-522af60a>(.*?)</span>'\
                  '</p>'

# REGEX_RANK_TEAM = regex_rank_team_.format(rank="1")
