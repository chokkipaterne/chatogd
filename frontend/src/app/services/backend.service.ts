import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ConstantsService } from '../helpers/constants.service';

@Injectable({
  providedIn: 'root',
})
export class BackendService {
  constructor(
    private http: HttpClient,
    private constantService: ConstantsService
  ) {}

  getPortals() {
    return this.http.get<any>(`${this.constantService.baseApiUrl}/portals`);
  }

  dataQuality(formData: any) {
    return this.http.post<any>(
      `${this.constantService.baseApiUrl}/dataquality`,
      formData
    );
  }
}
