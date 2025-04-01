from django.shortcuts import render,redirect


def signin_required(fn):

    def wrapper(request,*args,**kwargs):

        if not request.user.is_authenticated:

            return redirect("login")
        else:
            return fn(request,*args,**kwargs)
    return wrapper