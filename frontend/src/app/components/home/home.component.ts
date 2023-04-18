import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { first } from 'rxjs/operators';
import { AlertService } from '../../services/alert.service';
import { BackendService } from '../../services/backend.service';
import { ConstantsService } from '../../helpers/constants.service';
import * as _ from 'lodash';
declare var $: any;

export enum CHATINTERACTIONS {
  SelectPortal = 0,
  SelectDataset = 1,
}

/*Inspired from https://essentialistengineer.com/how-to-build-a-chat-ui-with-angular/ */
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
})
export class HomeComponent implements OnInit {
  listPortals: any = [];
  chatInteraction: number = CHATINTERACTIONS.SelectPortal;
  statusLoad: boolean = false;
  chosenPortal: any;
  chosenDataset: any;
  quality: any;
  idDataset: any;
  metadataDimensions: any = [];
  dataDimensions: any = [];
  columns: any = [];
  initMetadataDimensions: any = [];
  initDataDimensions: any = [];
  initColumns: any = [];

  graphMd: boolean = true;
  graphMdDimension: boolean = false;
  graphMdMetric: boolean = false;
  graphDt: boolean = true;
  graphDtDimension: boolean = false;
  graphDtMetric: boolean = false;
  selectedMdDimension: any;
  selectedDtDimension: any;
  dataTitle: string = '';

  @ViewChild('chatListContainer') list?: ElementRef<HTMLDivElement>;

  @ViewChild('dqrep') rep?: ElementRef<HTMLDivElement>;
  chatInputMessage: string = '';
  human = {
    id: 1,
    profileImageUrl:
      'https://cdn.pixabay.com/photo/2017/07/18/23/23/user-2517433_960_720.png',
  };

  bot = {
    id: 2,
    profileImageUrl:
      'https://media.istockphoto.com/photos/3d-illustration-of-virtual-human-on-technology-background-picture-id1181533674?s=612x612',
  };

  chatMessages: {
    user: any;
    message: string;
  }[] = [
    {
      user: this.bot,
      message:
        "Hello, I'm ChatOGD, a chatbot that can help you to evaluate the data quality of your open dataset.",
    },
  ];
  initMessages: {
    user: any;
    message: string;
  }[] = [];

  dqBtn: boolean = true;

  constructor(
    private alertService: AlertService,
    private backendService: BackendService,
    private constantService: ConstantsService
  ) {}

  ngOnInit() {
    this.loadPortals();

    setInterval(function () {
      $(document).ready(function () {
        //for right or left click(any)
        $('.tooltipped').mousedown(function () {
          $('.material-tooltip').css('visibility', 'hidden');
        });
        // leaving after click in case you open link in new tab
        $('.tooltipped').mouseleave(function () {
          $('.material-tooltip').css('visibility', 'hidden');
        });
      });
    }, 4000);
  }

  loadPortals() {
    this.backendService
      .getPortals()
      .pipe(first())
      .subscribe(
        (data) => {
          this.listPortals = data;
          console.log(this.listPortals);
          this.choicePortal(true);
        },
        (error) => {
          this.alertService.error(error);
        }
      );
  }

  choicePortal(init = false) {
    let message =
      'Please choose from the list below the portal to which your dataset belongs.';

    this.listPortals.forEach((portal: any) => {
      message +=
        '<br/><a target="_blank" href="' +
        portal.more_details.link +
        '">' +
        portal.sequence +
        '. ' +
        portal.name +
        '</a>';
    });

    let messagebot = {
      user: this.bot,
      message: message,
    };
    this.chatMessages = [...this.chatMessages, messagebot];
    if (init) {
      this.initMessages = [...this.chatMessages];
    }
  }

  choiceDataset(init = false) {
    this.chatInteraction = CHATINTERACTIONS.SelectDataset;
    let message = '';
    let system_name = this.chosenPortal.system_name;
    if (system_name.includes('ods')) {
      message =
        'Please enter the identifier of your dataset.<br/>(Ref to FAQ to see how to get identifier)';
    } else if (system_name.includes('ckan')) {
      message =
        'Please enter the package and the resource of your dataset separted by a comma.<br/>(Ref to FAQ to see how to get these informations)';
    }

    let messagebot = {
      user: this.bot,
      message: message,
    };
    this.chatMessages = [...this.chatMessages, messagebot];
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  toInt(value: any) {
    return parseInt(value);
  }

  send() {
    this.chatMessages.push({
      message: this.chatInputMessage,
      user: this.human,
    });
    if (this.chatInteraction == CHATINTERACTIONS.SelectPortal) {
      this.statusLoad = true;
      let sequencePortal = parseInt(this.chatInputMessage);
      let portalIndex = this.listPortals.findIndex(
        (item: any) => item.sequence == sequencePortal
      );
      if (portalIndex >= 0) {
        this.chosenPortal = this.listPortals[portalIndex];
        this.choiceDataset();
      } else {
        this.alertService.error('There is no portal that matches your input');
        let messagebot = {
          user: this.bot,
          message: 'There is no portal that matches your input',
        };
        this.chatMessages = [...this.chatMessages, messagebot];
        this.choicePortal();
      }
      this.statusLoad = false;
    } else if (this.chatInteraction == CHATINTERACTIONS.SelectDataset) {
      this.chosenDataset = null;
      let dataset = this.chatInputMessage;
      this.idDataset = dataset;
      let formData = new FormData();
      formData.append('portal', this.chosenPortal.id);
      formData.append('dataset', dataset);
      this.statusLoad = true;
      this.backendService
        .dataQuality(formData)
        .pipe(first())
        .subscribe(
          (data) => {
            this.getResult(data, 1);
            this.statusLoad = false;
            let messagebot = {
              user: this.bot,
              message:
                'Data Quality generated sucessfully. Please setup our preferences under #User Preferences# button to only take into account in the quality assessment the dimensions, metrics and attributes you want.',
            };
            this.chatMessages = [...this.chatMessages, messagebot];
            setTimeout(() => {
              this.anotherDataset();
            }, 5000);
          },
          (error) => {
            this.alertService.error(error);
            let messagebot = {
              user: this.bot,
              message: error,
            };
            this.chatMessages = [...this.chatMessages, messagebot];
            this.choiceDataset();
            this.statusLoad = false;
          }
        );
    }
    this.chatInputMessage = '';
    this.scrollToBottom();
  }

  getResult(data: any, init: number = 1) {
    this.graphMd = true;
    this.graphMdDimension = false;
    this.graphMdMetric = false;
    this.selectedMdDimension = undefined;

    this.graphDt = true;
    this.graphDtDimension = false;
    this.graphDtMetric = false;
    this.selectedDtDimension = undefined;
    this.metadataDimensions = _.cloneDeep(data['metadata_dimensions']);
    this.dataDimensions = _.cloneDeep(data['data_dimensions']);
    this.columns = _.cloneDeep(data['columns']);

    if (init == 1) {
      this.initMetadataDimensions = _.cloneDeep(data['metadata_dimensions']);
      this.initDataDimensions = _.cloneDeep(data['data_dimensions']);
      this.initColumns = _.cloneDeep(data['columns']);
    }

    this.chosenDataset = data['dataset'];
    this.dataTitle = data['dataset']['dataset']['metas']['default']['title'];
    this.quality = data['quality'];
    this.dqBtn = true;
    setInterval(function () {
      $(document).ready(function () {
        $('.collapsible').collapsible();
      });
    }, 1000);

    setTimeout(function () {
      $(document).ready(function () {
        $('.gaugemeter').gaugeMeter();
        $('.tooltipped').tooltip();
        //for right or left click(any)
        $('.tooltipped').mousedown(function () {
          $('.material-tooltip').css('visibility', 'hidden');
        });
        // leaving after click in case you open link in new tab
        $('.tooltipped').mouseleave(function () {
          $('.material-tooltip').css('visibility', 'hidden');
        });
      });
    }, 1000);
  }

  anotherDataset() {
    let messagebot = {
      user: this.bot,
      message: 'Want to analyze another dataset? If yes.',
    };
    console.log(this.chatMessages);
    this.chatMessages = [...this.chatMessages, messagebot];
    this.choiceDataset();
  }

  moreDetailsMd() {
    this.graphMd = false;
    this.graphMdDimension = true;
    this.graphMdMetric = false;
    this.selectedMdDimension = undefined;
    setTimeout(function () {
      $(document).ready(function () {
        $('.tooltipped').tooltip();
      });
    }, 1000);
  }

  moreDetailsDt() {
    this.graphDt = false;
    this.graphDtDimension = true;
    this.graphDtMetric = false;
    this.selectedDtDimension = undefined;
    setTimeout(function () {
      $(document).ready(function () {
        $('.tooltipped').tooltip();
      });
    }, 1000);
  }

  backMd() {
    this.graphMd = true;
    this.graphMdDimension = false;
    this.graphMdMetric = false;
    this.selectedMdDimension = undefined;
    setTimeout(function () {
      $(document).ready(function () {
        $('.gaugemeter').gaugeMeter();
      });
    }, 1000);
  }

  backDt() {
    this.graphDt = true;
    this.graphDtDimension = false;
    this.graphDtMetric = false;
    this.selectedDtDimension = undefined;
    setTimeout(function () {
      $(document).ready(function () {
        $('.gaugemeter').gaugeMeter();
      });
    }, 1000);
  }

  backMdDimension() {
    this.graphMd = false;
    this.graphMdDimension = true;
    this.graphMdMetric = false;
    this.selectedMdDimension = undefined;
    setTimeout(function () {
      $(document).ready(function () {
        $('.tooltipped').tooltip();
      });
    }, 1000);
  }

  backDtDimension() {
    this.graphDt = false;
    this.graphDtDimension = true;
    this.graphDtMetric = false;
    this.selectedDtDimension = undefined;
    setTimeout(function () {
      $(document).ready(function () {
        $('.tooltipped').tooltip();
      });
    }, 1000);
  }

  metricsMd(dim: any) {
    let dimIndex = this.metadataDimensions.findIndex(
      (item: any) => item.id == dim.id
    );
    if (dimIndex >= 0) {
      this.selectedMdDimension = this.metadataDimensions[dimIndex];
    }
    this.graphMd = false;
    this.graphMdDimension = false;
    this.graphMdMetric = true;
    setTimeout(function () {
      $(document).ready(function () {
        $('.tooltipped').tooltip();
      });
    }, 1000);
  }

  metricsDt(dim: any) {
    let dimIndex = this.dataDimensions.findIndex(
      (item: any) => item.id == dim.id
    );
    if (dimIndex >= 0) {
      this.selectedDtDimension = this.dataDimensions[dimIndex];
    }
    this.graphDt = false;
    this.graphDtDimension = false;
    this.graphDtMetric = true;
    setTimeout(function () {
      $(document).ready(function () {
        $('.tooltipped').tooltip();
      });
    }, 1000);
  }

  valueQt(key: any) {
    if (key in this.quality) {
      return this.toInt(this.quality[key]);
    }
    return 0;
  }

  clearMessage() {
    this.chatMessages = [...this.initMessages];
    this.chatInteraction = CHATINTERACTIONS.SelectPortal;
    this.metadataDimensions = [];
    this.initMetadataDimensions = [];
    this.dataDimensions = [];
    this.initDataDimensions = [];
    this.columns = [];
    this.initColumns = [];
    this.chosenDataset = null;
    this.scrollToBottom();
  }

  scrollToBottom() {
    const maxScroll = this.list?.nativeElement.scrollHeight;
    this.list?.nativeElement.scrollTo({ top: maxScroll });
  }

  handleChkState(col: any) {
    console.log(this.columns);
  }

  updateMetadataMetrics(dim: any) {
    let dimIndex = this.metadataDimensions.findIndex(
      (item: any) => item.id == dim.id
    );
    if (dimIndex >= 0) {
      if (this.metadataDimensions[dimIndex].weight == 0) {
        this.metadataDimensions[dimIndex].metrics.forEach(
          (metric: any, index: any) => {
            this.metadataDimensions[dimIndex].metrics[index].weight = 0;
          }
        );
      }
      this.metadataDimensions = [...this.metadataDimensions];
    }
  }
  updateDataMetrics(dim: any) {
    let dimIndex = this.dataDimensions.findIndex(
      (item: any) => item.id == dim.id
    );
    if (dimIndex >= 0) {
      if (this.dataDimensions[dimIndex].weight == 0) {
        this.dataDimensions[dimIndex].metrics.forEach(
          (metric: any, index: any) => {
            this.dataDimensions[dimIndex].metrics[index].weight = 0;
          }
        );
      }
      this.dataDimensions = [...this.dataDimensions];
    }
  }
  resetMd() {
    this.metadataDimensions = _.cloneDeep(this.initMetadataDimensions);
  }
  resetDq() {
    this.dataDimensions = _.cloneDeep(this.initDataDimensions);
  }
  selectAll() {
    this.columns.forEach((col: any, index: any) => {
      this.columns[index].checked = true;
    });
    this.columns = [...this.columns];
  }
  deselectAll() {
    this.columns.forEach((col: any, index: any) => {
      this.columns[index].checked = false;
    });
    this.columns = [...this.columns];
  }
  zeroMd() {
    this.metadataDimensions.forEach((metric: any, dimIndex: any) => {
      this.metadataDimensions[dimIndex].weight = 0;
      this.metadataDimensions[dimIndex].metrics.forEach(
        (metric: any, index: any) => {
          this.metadataDimensions[dimIndex].metrics[index].weight = 0;
        }
      );
    });
    this.metadataDimensions = [...this.metadataDimensions];
  }
  zeroDq() {
    this.dataDimensions.forEach((metric: any, dimIndex: any) => {
      this.dataDimensions[dimIndex].weight = 0;
      this.dataDimensions[dimIndex].metrics.forEach(
        (metric: any, index: any) => {
          this.dataDimensions[dimIndex].metrics[index].weight = 0;
        }
      );
    });
    this.dataDimensions = [...this.dataDimensions];
  }
  switchBtn(value: boolean) {
    let oldBtn = this.dqBtn;
    this.dqBtn = value;
    if (oldBtn != value) {
      if (this.dqBtn) {
        this.handleUserPreferences();
        setTimeout(function () {
          $(document).ready(function () {
            $('.gaugemeter').gaugeMeter();
          });
        }, 1000);
      } else {
        setTimeout(function () {
          $(document).ready(function () {
            $('.tooltipped').tooltip();
          });
        }, 1000);
      }
    }
  }
  handleUserPreferences() {
    let dataset = this.idDataset;
    let formData = new FormData();
    formData.append('portal', this.chosenPortal.id);
    formData.append('dataset', dataset);
    formData.append(
      'metadata_dimensions',
      JSON.stringify(this.metadataDimensions)
    );
    formData.append('data_dimensions', JSON.stringify(this.dataDimensions));
    formData.append('columns', JSON.stringify(this.columns));
    this.statusLoad = true;
    this.backendService
      .dataQuality(formData)
      .pipe(first())
      .subscribe(
        (data) => {
          this.getResult(data, 0);
          this.statusLoad = false;
          let messagebot = {
            user: this.bot,
            message: 'Data Quality updated sucessfully.',
          };
          this.chatMessages = [...this.chatMessages, messagebot];
          setTimeout(() => {
            this.anotherDataset();
          }, 5000);
        },
        (error) => {
          this.alertService.error(error);
          let messagebot = {
            user: this.bot,
            message: error,
          };
          this.chatMessages = [...this.chatMessages, messagebot];
          this.choiceDataset();
          this.statusLoad = false;
        }
      );
  }
}
