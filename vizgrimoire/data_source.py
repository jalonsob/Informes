## Copyright (C) 2012, 2013 Bitergia
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details. 
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## This file is a part of GrimoireLib
##  (an Python library for the MetricsGrimoire and vizGrimoire systems)
##
##
## Authors:
##   Alvaro del Castillo <acs@bitergia.com>

""" DataSource offers the API to get aggregated, evolutionary and top data with filter 
    support for Grimoire supported data sources """ 

import logging, os
from vizgrimoire.metrics.query_builder import DSQuery, ITSQuery, MLSQuery
from vizgrimoire.GrimoireUtils import createJSON
from vizgrimoire.metrics.metrics_filter import MetricFilters
from vizgrimoire.filter import Filter

class DataSource(object):
    _bots = []
    _metrics_set = []
    _global_filter = None

    @staticmethod
    def get_name():
        """Get the name"""
        raise NotImplementedError

    @staticmethod
    def get_bots():
        """Get the bots to be filtered"""
        return DataSource._bots

    @staticmethod
    def set_bots(ds_bots):
        """Set the bots to be filtered"""
        DataSource._bots = ds_bots


    @staticmethod
    def get_global_filter(ds):
        """Get the global filter to be applied to all metrics"""
        return ds._global_filter

    @staticmethod
    def set_global_filter(ds, global_filter):
        """
            Set the global filter to be applied to all metrics
            Format: its_global_filter = ['ticket_type,,ticket_type','"Bug",,"New Feature"']
        """
        # We need to parse filter string to convert to type_analysis
        global_filter = global_filter.replace("[","").replace("]","")
        type_analysis = global_filter.split("','")
        last = len(type_analysis)
        type_analysis[0] = type_analysis[0][1:]
        type_analysis[last-1] = type_analysis[last-1][0:-1]

        ds._global_filter = type_analysis

    @staticmethod
    def get_db_name():
        """Get the name of the database with the data"""
        raise NotImplementedError

    @classmethod
    def get_date_init(cls, startdate, enddate, identities_db, type_analysis):
        """Get the date of the first activity in the data source"""
        dinit = None
        first_date = cls.get_metrics("first_date", cls)
        if first_date is not None:
            type_analysis_orig = first_date.filters.type_analysis
            first_date.filters.type_analysis = type_analysis
            dinit = first_date.get_agg()
            first_date.filters.type_analysis = type_analysis_orig
        return dinit

    @classmethod
    def get_date_end(cls, startdate, enddate, identities_db, type_analysis):
        """Get the date of the last activity in the data source"""
        dlast = None
        last_date = cls.get_metrics("last_date", cls)
        if last_date is not None:
            type_analysis_orig = last_date.filters.type_analysis
            last_date.filters.type_analysis = type_analysis
            dlast = last_date.get_agg()
            last_date.filters.type_analysis = type_analysis_orig
        return dlast

    @staticmethod
    def get_url():
        """Get the URL from which the data source was gathered"""
        pass

    def get_evolutionary_filename (self, filter_ = None):
        """Get the filename used to store evolutionary data"""
        name = None
        if (filter_ is None):
            name = self.get_name()+"-evolutionary.json"
        else:
            name = filter_.get_evolutionary_filename(self)
        return name

    @staticmethod
    def get_evolutionary_data (period, startdate, enddate, identities_db, filter_ = None):
        """Get the evolutionary data"""
        raise NotImplementedError

    @staticmethod
    def create_evolutionary_report (period, startdate, enddate, destdir, identities_db, filter_ = None):
        """Create the evolutionary data report"""
        raise NotImplementedError

    def get_agg_filename (self, filter_ = None):
        """Get the filename used to store aggregated data"""
        name = None
        if (filter_ is None):
            name = self.get_name()+"-static.json"
        else:
            name = filter_.get_static_filename(self)
        return name

    @staticmethod
    def get_agg_data (period, startdate, enddate, identities_db, filter_ = None):
        """Get the aggregated data"""
        raise NotImplementedError

    @staticmethod
    def create_agg_report (period, startdate, enddate, destdir, identities_db, type_analysis = None):
        """Create the aggregated report"""
        raise NotImplementedError

    @staticmethod
    def get_events():
        """Get the alerts detected"""
        raise NotImplementedError

    def get_top_filename (self, filter_ = None):
        """Get the filename used to store top data"""
        name = None
        if filter_ is None:
            name = self.get_name()+"-top.json"
        else:
            name = filter_.get_top_filename(self)
        return name

    @staticmethod
    def get_top_metrics ():
        """Get the top metric names"""
        raise NotImplementedError

    @staticmethod
    def get_top_data (startdate, enddate, identities_db, filter_, npeople):
        """Get the top data"""
        raise NotImplementedError

    @staticmethod
    def create_top_report (startdate, enddate, destdir, identities_db):
        """Create the top data report"""
        raise NotImplementedError

    @staticmethod
    def get_filter_items(filter_, period, startdate, enddate, identities_db):
        """Get the items in the data source available for the filter"""
        raise NotImplementedError

    @staticmethod
    def get_filter_bots(filter_):
        from vizgrimoire.report import Report
        bots = []

        # If not using Report (automator) bots are not supported.
        if Report.get_config() == None:
            return bots

        if filter_.get_name_plural()+'_out' in Report.get_config()['r']:
            fbots = Report.get_config()['r'][filter_.get_name_plural()+'_out']
            bots = fbots.split(",")
            logging.info("BOTS for " + filter_.get_name_plural())
            logging.info(bots)
        return bots

    @staticmethod
    def get_filter_summary(filter_, period, startdate, enddate, identities_db, limit):
        """Get items with a summary for the data source available for the filter"""
        raise NotImplementedError

    @staticmethod
    def create_filter_report(filter_, period, startdate, enddate, destdir, npeople, identities_db):
        """Create all files related to all filters in all data sources"""
        raise NotImplementedError

    @staticmethod
    def create_filter_report_all(filter_, period, startdate, enddate, destdir, npeople, identities_db):
        """Create all files related to all filters in all data sources using GROUP BY queries"""
        raise NotImplementedError

    @staticmethod
    def get_top_people_file(ds):
        """Get the filename used to store top people data"""
        return ds+"-people.json"

    @staticmethod
    def get_top_people(startdate, enddate, identities_db, npeople):
        """Get top people data"""
        raise NotImplementedError

    def get_person_evol_file(self, uuid):
        """Get the filename used to store evolutionary data for a person activity"""
        ds = self.get_name()
        name = "people-"+str(uuid)+"-"+ds+"-evolutionary.json"
        return name

    @staticmethod
    def get_person_evol(uuid, period, startdate, enddate, identities_db, type_analysis):
        """Get the evolutionary data for a person activity"""
        raise NotImplementedError

    def get_person_agg_file(self, uuid):
        """Get the filename used to store aggregated data for a person activity"""
        ds = self.get_name()
        name = "people-"+str(uuid)+"-"+ds+"-static.json"
        return name

    @staticmethod
    def get_person_agg(uuid, startdate, enddate, identities_db, type_analysis):
        """Get aggregated data for a person activity"""
        raise NotImplementedError

    def create_people_report(self, period, startdate, enddate, destdir, npeople, identities_db, people_ids=None):
        """Create all files related to people activity (aggregated, evolutionary)"""
        fpeople = os.path.join(destdir,self.get_top_people_file(self.get_name()))
        if not people_ids:
            people = self.get_top_people(startdate, enddate, identities_db, npeople)
            if people is None: return
        else:
            people = people_ids

        createJSON(people, fpeople)

        for uuid in people :
            evol_data = self.get_person_evol(uuid, period, startdate, enddate,
                                            identities_db, type_analysis = None)
            fperson = os.path.join(destdir,self.get_person_evol_file(uuid))
            createJSON (evol_data, fperson)

            agg = self.get_person_agg(uuid, startdate, enddate,
                                     identities_db, type_analysis = None)
            fperson = os.path.join(destdir,self.get_person_agg_file(uuid))
            createJSON (agg, fperson)

    @staticmethod
    def create_r_reports(vizr, enddate, destdir):
        """Create all files related to R reports"""
        raise NotImplementedError

    @staticmethod
    def get_metrics_definition (DS):
        """Return all metrics definition available"""
        mdef = {}
        ds_name = DS.get_name()
        all_metrics = DS.get_metrics_set(DS)
        for item in all_metrics:
            ds_metric_id = ds_name+"_"+item.id
            mdef[ds_metric_id] = {
                "divid" : ds_metric_id,
                "column" : item.id,
                "name" :   item.name,
                "desc" : item.desc
            }
            # old params to be removed in sync with clients
            if hasattr(item, 'envision'):
                mdef[ds_metric_id]['envision'] = item.envision
            if hasattr(item, 'action'):
                mdef[ds_metric_id]['action'] = item.action
        return mdef

    @staticmethod
    def get_metrics_set(ds):
        """Return all metrics objects available"""
        return ds._metrics_set

    @staticmethod
    def set_metrics_set(ds, metrics_set):
        """Set all metrics objects available"""
        ds._metrics_set = metrics_set

    @staticmethod
    def add_metrics(metrics, ds):
        ds._metrics_set.append(metrics)

    @staticmethod
    def get_metrics(id, ds):
        metrics = None
        for item in ds._metrics_set:
            if item.id == id:
                metrics = item
        return metrics

    @staticmethod
    def get_studies_data(ds, period, startdate, enddate, evol):
        """ Get data from studies to be included in agg and evol global JSONs  """
        from vizgrimoire.report import Report
        data = {}

        db_identities = Report.get_config()['generic']['db_identities']
        dbuser = Report.get_config()['generic']['db_user']
        dbpass = Report.get_config()['generic']['db_password']

        studies = Report.get_studies()

        metric_filters = Report.get_default_filter()

        ds_dbname = ds.get_db_name()
        dbname = Report.get_config()['generic'][ds_dbname]
        dsquery = ds.get_query_builder()
        dbcon = dsquery(dbuser, dbpass, dbname, db_identities)
        evol_txt = "evol"
        if not evol: evol_txt = "agg"
        logging.info("Creating studies for " + ds.get_name() + " " + evol_txt)
        for study in studies:
            try:
                obj = study(dbcon, metric_filters)
                if evol:
                    res = obj.get_ts(ds)
                else:
                    res = obj.get_agg(ds)
                if res is not None:
                    data = dict(res.items() + data.items())
            except TypeError:
                # logging.info(study.id + " does no support standard API. Not used.")
                pass

        return data

    @classmethod
    def get_metrics_data(DS, period, startdate, enddate, identities_db,
                         filter_ = None, evol = False):
        """ Get basic data from all core metrics """
        from vizgrimoire.GrimoireUtils import fill_and_order_items
        from vizgrimoire.ITS import ITS
        from vizgrimoire.MLS import MLS
        data = {}
        dsquery = DSQuery
        if DS == ITS: dsquery = ITSQuery
        if DS == MLS: dsquery = MLSQuery

        from vizgrimoire.report import Report
        automator = Report.get_config()

        if evol:
            metrics_on = DS.get_metrics_core_ts()
            automator_metrics = DS.get_name()+"_metrics_ts"
        else:
            metrics_on = DS.get_metrics_core_agg()
            automator_metrics = DS.get_name()+"_metrics_agg"

        if automator_metrics in automator['r']:
            metrics_on = automator['r'][automator_metrics].split(",")

        people_out = []
        if "people_out" in Report.get_config()['r']:
            people_out = Report.get_config()['r']["people_out"]
            people_out = people_out.split(",")


        type_analysis = None
        if filter_ is not None:
            type_analysis = filter_.get_type_analysis()

        if type_analysis and type_analysis[1] is None:
            # We need the items for filling later values in group by queries
            items = DS.get_filter_items(filter_, startdate, enddate, identities_db)
            if items is None: return data
            items = items.pop('name')

        if DS.get_name()+"_startdate" in Report.get_config()['r']:
            startdate = Report.get_config()['r'][DS.get_name()+"_startdate"]
        if DS.get_name()+"_enddate" in Report.get_config()['r']:
            enddate = Report.get_config()['r'][DS.get_name()+"_enddate"]
        # TODO: the hardcoded 10 should be removed, and use instead the npeople provided
        #       in the config file.
        mfilter = MetricFilters(period, startdate, enddate, type_analysis, 10, people_out, None)
        metrics_reports = DS.get_metrics_core_reports()
        all_metrics = DS.get_metrics_set(DS)

        # Reports = filters metrics not available inside filters
        if type_analysis is None:
            from vizgrimoire.report import Report
            reports_on = Report.get_config()['r']['reports'].split(",")
            for r in metrics_reports:
                if r in reports_on: metrics_on += [r]

        for item in all_metrics:
            # print item
            if item.id not in metrics_on: continue
            mfilter_orig = item.filters
            mfilter.global_filter = mfilter_orig.global_filter
            mfilter.set_closed_condition(mfilter_orig.closed_condition)
            item.filters = mfilter
            if evol: mvalue = item.get_ts()
            else:    mvalue = item.get_agg()

            if type_analysis and type_analysis[1] is None and mvalue:
                logging.info(item.id)
                id_field = None
                # Support for combined filters
                for idf in mvalue.keys():
                    if "CONCAT(" in idf:
                        id_field = idf
                        break
                if id_field is None:
                    id_field = dsquery.get_group_field_alias(type_analysis[0])
                mvalue = fill_and_order_items(items, mvalue, id_field,
                                              evol, period, startdate, enddate)
            data = dict(data.items() + mvalue.items())

            item.filters = mfilter_orig

        if not evol:
            init_date = DS.get_date_init(startdate, enddate, identities_db, type_analysis)
            end_date = DS.get_date_end(startdate, enddate, identities_db, type_analysis)

            if type_analysis and type_analysis[1] is None:
                if id_field is None:
                    id_field = dsquery.get_group_field_alias(type_analysis[0])
                init_date = fill_and_order_items(items, init_date, id_field,
                                                 evol, period, startdate, enddate)
                end_date = fill_and_order_items(items, end_date, id_field,
                                                evol, period, startdate, enddate)
            if init_date is None: init_date = {}
            if end_date is None: end_date = {}
            data = dict(data.items() + init_date.items() + end_date.items())

            # Tendencies
            metrics_trends = DS.get_metrics_core_trends()

            automator_metrics = DS.get_name()+"_metrics_trends"
            if automator_metrics in automator['r']:
                metrics_trends = automator['r'][automator_metrics].split(",")

            for i in [7,30,365]:
                for item in all_metrics:
                    if item.id not in metrics_trends: continue
                    mfilter_orig = item.filters
                    item.filters = mfilter
                    period_data = item.get_trends(enddate, i)
                    item.filters = mfilter_orig

                    if type_analysis and type_analysis[1] is None:
                        group_field = dsquery.get_group_field_alias(type_analysis[0])
                        period_data = fill_and_order_items(items, period_data, group_field)

                    data = dict(data.items() + period_data.items())

        return data

    @staticmethod
    def get_metrics_core_agg():
        """ Aggregation metrics core """
        raise NotImplementedError

    @staticmethod
    def get_metrics_core_ts():
        """ Time series metrics core """
        raise NotImplementedError

    @staticmethod
    def get_metrics_core_trends():
        """ Trends metrics core """
        raise NotImplementedError

    @staticmethod
    def get_metrics_core_reports():
        """ Reports metrics core: Only available if activated in automator conf. """
        return ["organizations","countries","domains"]

    @staticmethod
    def remove_filter_data():
        """Remove from the database all information about this filter (i.e. a repository)"""
        raise NotImplementedError

    @staticmethod
    def get_query_builder():
        """Class used to build queries to get metrics"""
        raise NotImplementedError

    @classmethod
    def convert_all_to_single(cls, data, filter_, destdir, evolutionary, period='month'):
        """ Convert a GROUP BY result to follow tradition individual JSON files """
        from vizgrimoire.SCM import SCM
        from vizgrimoire.ITS import ITS
        from vizgrimoire.SCR import SCR
        from vizgrimoire.MLS import MLS
        from vizgrimoire.filter import Filter

        if cls == ITS or cls == SCR:
            if 'url' in data.keys():
                data['name'] = data.pop('url')
                data['name'] = [item.replace('/', '_') for item in data['name']]
        elif cls == MLS:
            if 'mailing_list_url' in data.keys():
                data['name'] = data.pop('mailing_list_url')
                data['name'] = [item.replace('/', '_') for item in data['name']]
        if cls == ITS or cls == SCM:
            if filter_.get_name() in ["company+country","company+project"]:
                data['name'] = data.pop('filter')

        if not evolutionary:
            # First create the JSON with the list of items
            item_list = {}
            fn = os.path.join(destdir, filter_.get_filename(cls))
            if cls == SCM:
                fields = ["authors_365","name","commits_365"]
            elif cls == ITS:
                fields = ["closed_365","closers_365", "name"]
            elif cls == MLS:
                fields = ["sent_365","senders_365", "name"]
            elif cls == SCR:
                fields = ["submitted","review_time_days_median","review_time_pending_upload_ReviewsWaitingForReviewer_days_median", "name"]
            else:
                fields = ["name"]
            for field in fields:
                if field in data:
                    item_list[field] = data[field]
            createJSON(item_list, fn)
        # Items files
        ts_fields = ['unixtime','id','date',period]
        # Not metrics fields
        no_metrics_fields = ['filter_type']
        for i in range(0,len(data['name'])):
            item_metrics = {}
            item = data['name'][i]
            for metric in data:
                if metric == "name": continue
                if metric in ts_fields+no_metrics_fields: continue
                if len(data[metric])<len(data['name']):
                    logging.error(cls.get_name()+" "+metric + " not supported in GROUP BY. Not included")
                    continue
                if evolutionary:
                    if not isinstance(data[metric][i], list):
                        logging.error(cls.get_name()+" "+metric + " evol not supported in GROUP BY. Not included")
                        continue
                item_metrics[metric] = data[metric][i]
            filter_item = Filter(filter_.get_name(), item)
            if evolutionary:
                for field in ts_fields:
                    # Shared time series fields
                    item_metrics[field] = data[field]
                fn = os.path.join(destdir, filter_item.get_evolutionary_filename(cls()))
            else:
                fn = os.path.join(destdir, filter_item.get_static_filename(cls()))
            createJSON(item_metrics, fn)

    @classmethod
    def ages_study_com (ds, items, period,
                        startdate, enddate, destdir):
        """Perform ages study for companies, if it is specified in Report.

        Produces JSON files for those studies.

        Parameters
        ----------

        ds: { SCM | ITS | MLS }
           Data source
        items: ??
           Items
        period: ??
           Period
        startdate: ??
           Start date
        enddate: ??
           End date
        destdir: string
           Directory for writing the JSON files
        """

        from vizgrimoire.report import Report
        filter_name = "company"
        studies = Report.get_studies()
        ages = None
        for study in studies:
            if study.id == "ages":
                ages = study

        if ages is not None:
            # Get config parameters for producing a connection
            # to the database
            config = Report.get_config()
            db_identities = config['generic']['db_identities']
            dbuser = config['generic']['db_user']
            dbpass = config['generic']['db_password']

            start_string = ds.get_name() + "_start_date"
            end_string = ds.get_name() + "_end_date"
            if start_string in config['r']:
                startdate = "'" + config['r'][start_string] + "'"
            if end_string in config['r']:
                enddate = "'" + config['r'][end_string] + "'"
            ds_dbname = ds.get_db_name()
            dbname = config['generic'][ds_dbname]
            dsquery = ds.get_query_builder()
            dbcon = dsquery(dbuser, dbpass, dbname, db_identities)

            for item in items :
                filter_item = Filter(filter_name, item)
                metric_filters = MetricFilters(
                    period, startdate, enddate,
                    filter_item.get_type_analysis()
                    )
                obj = ages(dbcon, metric_filters)
                res = obj.create_report(ds, destdir)
