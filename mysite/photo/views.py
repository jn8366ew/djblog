from django.shortcuts import render
from django.views.generic import ListView, DetailView
from photo.models import Album, Photo

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

# OwnerOnlyMixin 클래스는 로그인한 사용자가 콘텐츠 소유자인지 판별
# 유저가 소유권에 따라 컨텐츠를 수정할 수 있도록
# 로그인 사용자가 그 콘텐츠의 소유자인 경우에만 UpdateView 기능 동작
from mysite.views import OwnerOnlyMixin
# 폼셋: 동일한 폼 여러개로 구성된 폼
# 인라인 폼셋: 메인 폼에 딸려 있는 폼셋. 테이블간의 1:N인경우 N 테이블의 레코드
# 여러개를 한꺼번에 입력받기 위한 폼으로 사용
from photo.forms import PhotoInlineFormSet


class AlbumLV(ListView):
    model = Album

class AlbumDV(DetailView):
    model = Album

class PhotoDV(DetailView):
    model = Photo

# Create/Change-list/Update/Delete for Photo
# url for photo_add
class PhotoCV(LoginRequiredMixin, CreateView):
    model = Photo
    fields = ('album', 'title', 'image', 'description')
    success_url = reverse_lazy('photo:index')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

# url for photo_change
class PhotoChangeLV(LoginRequiredMixin, ListView):
    model = Photo
    template_name = 'photo/photo_change_list.html'

    def get_queryset(self):
        return Photo.objects.filter(owner=self.request.user)

class PhotoUV(OwnerOnlyMixin, UpdateView):
    model = Photo
    fields = ('album', 'title', 'image', 'description')
    success_url = reverse_lazy('photo:index')

class PhotoDelV(OwnerOnlyMixin, DeleteView):
    model = Photo
    success_url = reverse_lazy('photo:index')


# Change-list/Delete for Album
class AlbumChangeLV(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'photo/album_change_list.html'

    def get_queryset(self):
        return Album.objects.filter(owner=self.request.user)


class AlbumDelV(OwnerOnlyMixin, DeleteView):
    model = Album
    success_url = reverse_lazy('photo:index')


# InlineFormSet Create/Update for Album
class AlbumPhotoCV(LoginRequiredMixin, CreateView):
    model = Album
    fields = ('name', 'description')
    success_url = reverse_lazy('photo:index')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # POST 요청일경우 formset 컨텍스트 변수를 request.POST와 request.FILES를
        # 사용해 저장한다. request.FILES를 추가한 이유는 파일 업로드가 이루어지기 때문
        if self.request.POST:
            context['formset'] = PhotoInlineFormSet(self.request.POST, self.request.FILES)
        # Get 요청인경우 컨텍스트 변수에 빈 폼셋을 지정
        else:
            context['formset'] = PhotoInlineFormSet()
        return context


    # 폼에 입력된 내용에 대해 유효성 검사를 수행
    # 에러 없는 경우 form_valid 메소드를 호출함
    def form_valid(self, form):
        # 현재 로그인 된 사용자의 User 객체를 onwer 필드에 할당한다
        form.instance.owner = self.request.user
        # get_context_data()를 호출해 formset 객체를 구한다.
        context = self.get_context_data()
        # 이 시점에서 formset은 유효성 검사 전, form 데이터는 유효성 검사를 통과함
        formset = context['formset']

        # 폼셋에 들어 있는 owner 필드에 현재 로그인 된 user의 객체를 할당한다.
        for photoform in formset:
            photoform.instance.owner = self.request.user

        # 폼셋이 유효한지 화인
        if formset.is_valid():
            # 폼 데이터를 테이블에 저장한다. 즉 엘범 레코드 하나를 생성. 
            self.object = form.save()
            # 폼셋의 메인 객체를 방금 테이블에 저장한 객체로 지정
            formset.instance = self.object
            # 폼셋의 데이터를 테이블에 저장
            # 즉 self.object = form.save()에서 생성한 앨범 레코드에 1:N관계로 연결된
            # 여러 개의 사진 레코드를 테이블에 저장
            formset.save()
            # 페이지를 앨범리스트로 이동시킨다.
            return redirect(self.get_success_url())

        # 폼셋의 데이터가 유효하지 않을시 다시 메인 폼 및 인라인 폼셋을 출력한다.
        # 이 때의 폼과 폼셋에 직전에 사용자가 입력한 데이터를 다시 보여준다.
        else:
            return self.render_to_response(self.get_context_data(form=form))


# 책설명: OwnerOnlyMixin 클래스에 의해 앨범 소유자만 정상 처리됨
# UpdateView 클래스를 상속받는 클래스는 예제처럼 중요한 몇가지 클래스 속성만
# 정의하면 기존 레코드 중 지정된 레코드 하나에 대한 내용을 폼으로 보여주고
# 폼에서 수정 입력된 내용에서 에러여부 체크 -> 없으면 입력된 내용으로 테이블의 레코드 수정
class AlbumPhotoUV(OwnerOnlyMixin, UpdateView):
    # Update 기능을 적용할 대상 테이블을 지정
    model = Album
    # 엘범 테이블의 특정 필드를로 폼을 구성해 화면에 보여줌
    fields = ('name', 'description')
    # 수정 처리 성공한 이후에 리다이렉트할 URL을 지정
    success_url = reverse_lazy('photo:index')

    # get_context_data 메소드 오버라이드, 추가적인 컨텍스트 변수 정의를 위해.
    def get_context_data(self, **kwargs):
        # 부모클래스의 메소드를 호출 -> 기본 컨텍스트 변수를 설정한다.
        # 기본 컨텍스트 변수 이외에 메인 폼도 컨텍스트 변수에 추가
        context = super().get_context_data(**kwargs)
        # POST 요청인 경우 formset 컨텍스트 변수를 request.POST와 request.FILES 파라미터를 사용해
        # 지정한다. instance 파라미터에 현재의 앨범 객체를 지정한다.
        if self.request.POST:
            context['formset'] = PhotoInlineFormSet(self.request.POST, self.request.FILES, instance=self.object)
        # Get 일경우, formset 컨텍스트 변수에 현재의 앨범 객체와 연결된 폼셋을 지정한다.
        else:
            context['formset'] = PhotoInlineFormSet(instance=self.object)

        return context


    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.isinstance = self.object
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))



