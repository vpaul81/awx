import React from 'react';
import { act } from 'react-dom/test-utils';
import { createMemoryHistory } from 'history';
import { UsersAPI } from 'api';
import {
  mountWithContexts,
  waitForElement,
} from '../../../../testUtils/enzymeHelpers';
import UserDetail from './UserDetail';
import mockDetails from '../data.user.json';

jest.mock('../../../api');

describe('<UserDetail />', () => {
  test('initially renders successfully', () => {
    mountWithContexts(<UserDetail user={mockDetails} />);
  });

  test('should render Details', () => {
    const wrapper = mountWithContexts(<UserDetail user={mockDetails} />);
    function assertDetail(label, value) {
      expect(wrapper.find(`Detail[label="${label}"] dt`).text()).toBe(label);
      expect(wrapper.find(`Detail[label="${label}"] dd`).text()).toBe(value);
    }

    assertDetail('Username', mockDetails.username);
    assertDetail('Email', mockDetails.email);
    assertDetail('First Name', mockDetails.first_name);
    assertDetail('Last Name', mockDetails.last_name);
    assertDetail('User Type', 'System Administrator');
    assertDetail('Last Login', `2019-11-04, 23:12:36`);
    assertDetail('Created', `2019-10-28, 15:01:07`);
    assertDetail('Last Modified', `2021-07-12, 19:08:33`);
    assertDetail('Type', `SOCIAL`);
  });

  test('User Type Detail should render expected strings', async () => {
    let wrapper;
    wrapper = mountWithContexts(
      <UserDetail
        user={{
          ...mockDetails,
          is_superuser: false,
          is_system_auditor: true,
        }}
      />
    );
    expect(wrapper.find(`Detail[label="User Type"] dd`).text()).toBe(
      'System Auditor'
    );

    wrapper = mountWithContexts(
      <UserDetail
        user={{
          ...mockDetails,
          is_superuser: false,
          is_system_auditor: false,
        }}
      />
    );
    expect(wrapper.find(`Detail[label="User Type"] dd`).text()).toBe(
      'Normal User'
    );
  });

  test('should show edit button for users with edit permission', async () => {
    const wrapper = mountWithContexts(<UserDetail user={mockDetails} />);
    const editButton = await waitForElement(
      wrapper,
      'UserDetail Button[aria-label="edit"]'
    );
    expect(editButton.text()).toEqual('Edit');
    expect(editButton.prop('to')).toBe(`/users/${mockDetails.id}/edit`);
  });

  test('should hide edit button for users without edit permission', async () => {
    const wrapper = mountWithContexts(
      <UserDetail
        user={{
          ...mockDetails,
          summary_fields: {
            user_capabilities: {
              edit: false,
            },
          },
        }}
      />
    );
    await waitForElement(wrapper, 'UserDetail');
    expect(wrapper.find('UserDetail Button[aria-label="edit"]').length).toBe(0);
  });

  test('edit button should navigate to user edit', () => {
    const history = createMemoryHistory();
    const wrapper = mountWithContexts(<UserDetail user={mockDetails} />, {
      context: { router: { history } },
    });
    expect(wrapper.find('Button[aria-label="edit"]').length).toBe(1);
    wrapper
      .find('Button[aria-label="edit"] Link')
      .simulate('click', { button: 0 });
    expect(history.location.pathname).toEqual('/users/1/edit');
  });

  test('expected api call is made for delete', async () => {
    const wrapper = mountWithContexts(<UserDetail user={mockDetails} />);
    await waitForElement(wrapper, 'UserDetail Button[aria-label="Delete"]');
    await act(async () => {
      wrapper.find('DeleteButton').invoke('onConfirm')();
    });
    expect(UsersAPI.destroy).toHaveBeenCalledTimes(1);
  });

  test('Error dialog shown for failed deletion', async () => {
    UsersAPI.destroy.mockImplementationOnce(() => Promise.reject(new Error()));
    const wrapper = mountWithContexts(<UserDetail user={mockDetails} />);
    await waitForElement(wrapper, 'UserDetail Button[aria-label="Delete"]');
    await act(async () => {
      wrapper.find('DeleteButton').invoke('onConfirm')();
    });
    await waitForElement(
      wrapper,
      'Modal[title="Error!"]',
      (el) => el.length === 1
    );
    await act(async () => {
      wrapper.find('Modal[title="Error!"]').invoke('onClose')();
    });
    await waitForElement(
      wrapper,
      'Modal[title="Error!"]',
      (el) => el.length === 0
    );
  });
});
