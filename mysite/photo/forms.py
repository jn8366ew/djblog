# 폼셋이란 동일한 폼 여러 개로 구성된 폼을 의미
# 인라인 폼셋은 메인폼에 딸려 있는 하위 폼셋을 의미
# 테이블간의 관계가 1:N 인경우 N테이블의 레코드를 여러개를 한꺼번에 받기 위해 사용

from django.forms import inlineformset_factory
from photo.models import Album, Photo

PhotoInlineFormSet = inlineformset_factory(Album, Photo,
                                           fields = ['image', 'title', 'description'],
                                           extra = 2)

