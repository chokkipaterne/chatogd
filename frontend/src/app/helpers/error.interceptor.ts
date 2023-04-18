import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor() {}

  intercept(
    request: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError((err) => {
        var error = err.statusText;
        console.log(err);
        if (err.error.message) {
          error = err.error.message;
        } else if (err.message) {
          error = err.message;
        } else if (err.statusText) {
          error = err.statusText;
        } else if (err.error) {
          if (Array.isArray(err.error)) {
            err.error.forEach((element: any) => {
              error += '<br/>' + element;
            });
          } else if (typeof err.error === 'string') {
            error += '<br/>' + err.error;
          } else if (typeof err.error === 'object') {
            for (var key of Object.keys(err.error)) {
              if (Array.isArray(err.error[key])) {
                err.error[key].forEach((element: any) => {
                  error += '<br/>' + element;
                });
              } else if (typeof err.error[key] === 'string') {
                error += '<br/>' + err.error[key];
              }
            }
          }
        }
        return throwError(error);
      })
    );
  }
}
