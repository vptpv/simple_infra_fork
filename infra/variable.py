# возможно, скоро пригодится
def node_rename(reader):
    for line in reader:
        hostname_x = hostname(line['name'].strip())
        temp_x = nb.dcim.devices.get(name=hostname_x)
        if temp_x is None:
            print(f"{hostname_x}\tне найден")
        else:
            f_unit = first_unit(temp_x.parent_device.name)
            node = int(temp_x.parent_device.device_bay.name[-1])
            hostname_y = f"{hostname_x[0:3]}{temp_x.parent_device.name[-6:-3]}{str(int(temp_x.parent_device.name[-3:])-f_unit+(node-1))}"
            # print(hostname_y)
            comment = line['comments'].strip() + ' // ' +temp_x.comments
            temp_y = nb.dcim.devices.get(name=hostname_y)
            if temp_y is None:
                temp_x.update({
                    'name': hostname_y,
                    'comments': comment
                })
                print(f"{hostname_x}\t{hostname_y}\t{temp_x.parent_device.name}")
            else:
                print(f"{hostname_x}\t{hostname_y}\tуже существует")

def set_task_hosts(reader):
    for line in reader:
        url = f"{api_domain}/api/hosts?$filter=HostName eq '{line['old_name']}'"
        r = requests.get(url, cookies=get_cookie())
        json_1 = json.loads(r.text)
        try:
            hostId = str(json_1[0]["Id"])
            hostName = str(json_1[0]["HostName"])
        except IndexError:
            print(f"{line['old_name']} - не в стойке")
        else:
            if line['task'] != '':
                set_task(hostId, line['task'])
            print(f"{line['old_name']}\t{line['task']}")

def set_task(cookie, hostId, task):
    url = f"{api_domain}/api/hosts/{hostId}/update-task-requests"
    payload = {
        "Task": task
        # "TaskName": task
    }
    r = requests.post(url, cookies=cookie, data=json.dumps(payload), headers=headers)
    print(r.status_code)
    if r.status_code == 200:
        print('что-то получилось')

# совсем не то что было нужно
def set_org_unit_name(cookie, reader):
    url = f"{api_domain}/api/hosts/org-unit/batch-change"
    payload = [{
        "HostNames": [],
        # "HostName": line['old_name'],
        "OrgUnitName": "UMAgency",
        "Task": "VKENG-2964"
    }]
    for line in reader:
        payload[0]["HostNames"].append(line['new_name'])
    # pprint(payload)
    r = requests.post(url, cookies=cookie, data=json.dumps(payload[0]), headers=headers)
    if r.status_code == 200:
        print(f"вроде присвоились")
    else:
        print(r.status_code)

# тестовая выгрузка зипа
def get_zip_2(cookie):
    select = 'HardwareSubTypeName,HardwareModelName,HardwareModelId,SAPMaterialNumber,InstalledInto,DataCenterLocationName'
    # select = "ApproximateUseTimeHours,BalanceUnitId,Comment,DataCenterId,DataCenterLocationId,HardwareModelId,HardwareTypeId,HostLinkConfirmed,HostLinkedDateTime,HostName,HostOrgUnitId,InstallationTask,InstalledDate,InstalledInto,InstalledIntoId,IsActual,IsAsset,IsCurrentlyInUse,IsInTransit,IsRepairInProgress,IsUnregistered,OrgUnitId,OrgUnitName,OrgUnitPartnerId,OrgUnitPartnerName,OrgUnitStockId,ParentHasSubject,PartnerId,SAPMaterialNumber"
    # select = "BalanceUnitId,Comment,DataCenterId,DataCenterLocationId,HardwareModelId,HardwareTypeId,HostLinkConfirmed,HostLinkedDateTime,HostName,HostOrgUnitId,InstalledDate,InstalledInto,InstalledIntoId,IsActual,IsAsset,IsCurrentlyInUse,IsInTransit,IsRepairInProgress,IsUnregistered,OrgUnitId,OrgUnitName,OrgUnitPartnerId,OrgUnitPartnerName,OrgUnitStockId,ParentHasSubject,PartnerId,SAPMaterialNumber"
    # select = 'AccountedDateTime,ApproximateUseTimeHours,BalanceUnitId,BalanceUnitName,Comment,DataCenterId,DataCenterLocationId,DataCenterLocationName,DataCenterName,DecommissioningDate,DisposalDate,FirstStockDateTime,FirstUnit,HardwareAddressIpmi,HardwareAddresses,HardwareConfigurationId,HardwareConfigurationName,HardwareModelId,HardwareModelName,HardwareOriginalModelId,HardwareOriginalModelName,HardwareSubTypeId,HardwareSubTypeName,HardwareTypeId,HardwareTypeName,HostId,HostLinkConfirmed,HostLinkedDateTime,HostName,HostOrgUnitId,ImeiList,InstallationTask,InstalledDate,InstalledInto,InstalledIntoId,IsActual,IsAsset,IsCurrentlyInUse,IsInTransit,IsRepairInProgress,IsUnregistered,LocationDateTime,OrgUnitId,OrgUnitName,OrgUnitPartnerId,OrgUnitPartnerName,OrgUnitStockId,ParentHasSubject,PartnerId,Rack,RackId,RackRow,RackRowId,RentAllowed,RepairingTask,ReservationTask,ReservedDate,ReservedUser,ReservedUserId,SAPMaterialNumber,SapCommissioningId,SapCommissioningState,SapCommissioningStateId,SapDocumentDate,SapDocumentId,SapHwItemDocumentId,SapPartnerId,SapPartnerName,SerialNumber,SupplyId,Tasks,UnitQuantity,VkNetBoxDeviceId,WorkTask'
    repair = " and IsRepairInProgress eq false"
    model = " and HardwareModelId eq 710"
    location = " and DataCenterLocationName eq 'ICVA'"
    # location = ""
    installed = " and InstalledDate eq null and InstalledInto eq null"
    filter_ = f"$filter=HostName eq null and IsActual eq true and IsInTransit eq false{model}{location}{installed}"
    # filter_ = f"$filter=HostName eq null and IsInTransit eq false{model}{location}{installed}"
    url = f"{api_domain}/api/hardware-items?$select={select}&{filter_}"
    # url = f"{api_domain}/api/hardware-items?$filter={filter_}"
    print(url)
    r = requests.get(url, cookies=cookie)
    json_1 = json.loads(r.text)
    dict_ = {}
    for x in json_1:
        if x.get('InstalledInto') is None:
            if dict_.get(json.dumps(x), 0) == 0:
                dict_.update([(json.dumps(x),1)])
            else:
                dict_[json.dumps(x)]+=1
    list_ = []
    for x in dict_.items():
        y = json.loads(x[0])
        y.update([('Quantity',x[1])])
        # print(str((y)))
        list_.append(y)
    q = 0
    for x in list_:
        q = q+1
    pprint(q)
    pprint(list_)
