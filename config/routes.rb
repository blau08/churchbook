Rails.application.routes.draw do


  mount RailsAdmin::Engine => '/admin', as: 'rails_admin'
  get 'rooms/index'

  get 'schedules/index'

  devise_for :users do
    delete 'logout' => 'sessions#destroy', :as => :destroy_user_session
  end

  root 'homes#index'
  resources :students
  resources :demographics
  resources :homes
  resources :schedules
  resources :rooms

  resources :photos, only: [:index, :show, :new, :create, :destroy]

end
