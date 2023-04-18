import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { AlertService } from '../../services/alert.service';
import { ConstantsService } from '../../helpers/constants.service';
declare var $: any;
declare var M: any;
@Component({
  selector: 'app-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.scss'],
})
export class AlertComponent implements OnInit, OnDestroy {
  private subscription?: Subscription;
  message: any;

  constructor(
    private alertService: AlertService,
    private constantService: ConstantsService
  ) {}

  ngOnInit() {
    this.subscription = this.alertService.getAlert().subscribe((message) => {
      switch (message && message.type) {
        case 'success':
          message.cssClass = 'green darken-1 rounded';
          break;
        case 'error':
          message.cssClass = 'red darken-1 rounded';
          break;
      }
      this.message = message;
      var displayLength = this.constantService.toastDisplayLength;
      if (message && message.keep) {
        displayLength = this.constantService.toastDisplayLengthPlus;
      }
      if (this.message) {
        M.toast({
          displayLength: displayLength,
          html: this.message.text,
          classes: this.message.cssClass,
        });
        this.alertService.clear();
      }
    });
  }
  ngOnDestroy() {
    this.subscription?.unsubscribe();
  }
}
