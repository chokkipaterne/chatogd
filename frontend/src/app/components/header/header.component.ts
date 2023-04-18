import { Component, OnInit } from '@angular/core';
declare var $: any;
import { Router } from '@angular/router';
import { AlertService } from '../../services/alert.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
})
export class HeaderComponent implements OnInit {
  constructor(private router: Router, private alertService: AlertService) {}

  ngOnInit() {
    $(document).ready(function () {
      $('.sidenav').sidenav();
      $('.dropdown-trigger').dropdown();
      $('.sidenav-overlay').css('z-index', 1);
    });
  }

  closeSidenav() {
    $('.sidenav').sidenav('close');
  }
}
