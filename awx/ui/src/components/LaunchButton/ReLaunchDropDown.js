import React, { useState } from 'react';

import { t } from '@lingui/macro';
import {
  Dropdown,
  DropdownToggle,
  DropdownItem,
  DropdownPosition,
  DropdownSeparator,
  DropdownDirection,
} from '@patternfly/react-core';
import { CaretUpIcon, RocketIcon } from '@patternfly/react-icons';

function ReLaunchDropDown({
  isPrimary = false,
  isRelaunchJobType = false,
  handleRelaunch,
  isLaunching,
  id = 'relaunch-job',
  ouiaId,
}) {
  const [isOpen, setIsOpen] = useState(false);

  const onToggle = () => {
    setIsOpen((prev) => !prev);
  };

  const dropdownItems = [
    <DropdownItem
      ouiaId={`${ouiaId}-on`}
      aria-label={t`Relaunch on`}
      key="relaunch_on"
      component="div"
      isPlainText
    >
      {t`Relaunch on`}
    </DropdownItem>,
    <DropdownSeparator key="separator" />,
    <DropdownItem
      ouiaId={`${ouiaId}-all`}
      key="relaunch_all"
      aria-label={t`Relaunch all hosts`}
      component="button"
      onClick={() => {
        handleRelaunch({ hosts: 'all' });
      }}
      isDisabled={isLaunching}
    >
      {t`All`}
    </DropdownItem>,

    <DropdownItem
      ouiaId={`${ouiaId}-failed`}
      key="relaunch_failed"
      aria-label={t`Relaunch failed hosts`}
      component="button"
      onClick={() => {
        handleRelaunch({ hosts: 'failed' });
      }}
      isDisabled={isLaunching}
    >
      {t`Failed hosts`}
    </DropdownItem>,
  ];

  const dropdownItemsJobType = [
    <DropdownItem
      ouiaId={`${ouiaId}-on`}
      aria-label={t`Relaunch on`}
      key="relaunch_on"
      component="div"
      isPlainText
    >
      {t`Relaunch with job type`}
    </DropdownItem>,
    <DropdownSeparator key="separator" />,
    <DropdownItem
      ouiaId={`${ouiaId}-run-type`}
      key="relaunch_run_type"
      aria-label={t`Relaunch with job type run`}
      component="button"
      onClick={() => {
        handleRelaunch({ job_type: 'run' });
      }}
      isDisabled={isLaunching}
    >
      {t`Run`}
    </DropdownItem>,

    <DropdownItem
      ouiaId={`${ouiaId}-check-type`}
      key="relaunch_check_type"
      aria-label={t`Relaunch with job type check`}
      component="button"
      onClick={() => {
        handleRelaunch({ job_type: 'check' });
      }}
      isDisabled={isLaunching}
    >
      {t`Check`}
    </DropdownItem>,
  ];

  if (isPrimary) {
    return (
      <Dropdown
        ouiaId={ouiaId}
        position={DropdownPosition.left}
        direction={DropdownDirection.up}
        isOpen={isOpen}
        dropdownItems={isRelaunchJobType ? dropdownItemsJobType : dropdownItems}
        toggle={
          <DropdownToggle
            toggleIndicator={null}
            onToggle={onToggle}
            aria-label={t`relaunch jobs`}
            id={id}
            isPrimary
            ouiaId="relaunch-job-toggle"
          >
            {t`Relaunch`}
            <CaretUpIcon />
          </DropdownToggle>
        }
      />
    );
  }

  return (
    <Dropdown
      ouiaId={ouiaId}
      isPlain
      position={DropdownPosition.right}
      isOpen={isOpen}
      dropdownItems={dropdownItems}
      toggle={
        <DropdownToggle
          toggleIndicator={null}
          onToggle={onToggle}
          aria-label={t`relaunch jobs`}
          id={id}
          ouiaId="relaunch-job-toggle"
        >
          <RocketIcon />
        </DropdownToggle>
      }
    />
  );
}

export default ReLaunchDropDown;
