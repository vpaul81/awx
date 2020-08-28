import React from 'react';
import { t } from '@lingui/macro';
import { useField } from 'formik';
import InventoryStep from './InventoryStep';
import StepName from './StepName';

const STEP_ID = 'inventory';

export default function useInventoryStep(
  config,
  visitedSteps,
  i18n,
  loadedResource,
  currentResource
) {
  const [, meta] = useField('inventory');

  return {
    step: getStep(config, meta, i18n, visitedSteps),
    initialValues: getInitialValues(config, loadedResource, currentResource),
    isReady: true,
    contentError: null,
    formError: meta.error,
    setTouched: setFieldsTouched => {
      setFieldsTouched({
        inventory: true,
      });
    },
  };
}
function getStep(config, meta, i18n, visitedSteps) {
  if (!config.ask_inventory_on_launch) {
    return null;
  }
  return {
    id: STEP_ID,
    key: 3,
    name: (
      <StepName
        hasErrors={
          Object.keys(visitedSteps).includes(STEP_ID) &&
          (!meta.value || meta.error)
        }
      >
        {i18n._(t`Inventory`)}
      </StepName>
    ),
    component: <InventoryStep i18n={i18n} />,
    enableNext: true,
  };
}

function getInitialValues(config, loadedResource, currentResource) {

  if (
    !config.ask_inventory_on_launch &&
    !loadedResource?.summary_fields?.inventory
  ) {
    return {};
  }
  return {
    inventory:
      currentResource?.summary_fields?.inventory ||
      loadedResource?.summary_fields?.inventory ||
      null,
  };
}
