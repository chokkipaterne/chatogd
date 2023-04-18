import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ConstantsService {
  readonly baseApiUrl: string = 'http://localhost:8000/api';
  readonly toastDisplayLength: number = 5000;
  readonly toastDisplayLengthPlus: number = 6000;

  constructor() {}
}
