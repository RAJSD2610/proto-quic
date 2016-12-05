# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from page_sets.system_health import platforms
from page_sets.system_health import system_health_story

from page_sets.login_helpers import pinterest_login

from telemetry import decorators


class _BrowsingStory(system_health_story.SystemHealthStory):
  """Abstract base class for browsing stories.

  A browsing story visits items on the main page. Subclasses provide
  CSS selector to identify the items and implement interaction using
  the helper methods of this class.
  """

  IS_SINGLE_PAGE_APP = False
  ITEM_SELECTOR = NotImplemented
  ABSTRACT_STORY = True

  def _WaitForNavigation(self, action_runner):
    if not self.IS_SINGLE_PAGE_APP:
      action_runner.WaitForNavigate()

  def _NavigateToItem(self, action_runner, index):
    item_selector = 'document.querySelectorAll("%s")[%d]' % (
        self.ITEM_SELECTOR, index)
    # Only scrolls if element is not currently in viewport.
    action_runner.WaitForElement(element_function=item_selector)
    action_runner.ScrollPageToElement(element_function=item_selector)
    self._ClickLink(action_runner, item_selector)

  def _ClickLink(self, action_runner, element_function):
    action_runner.WaitForElement(element_function=element_function)
    action_runner.ClickElement(element_function=element_function)
    self._WaitForNavigation(action_runner)

  def _NavigateBack(self, action_runner):
    action_runner.ExecuteJavaScript('window.history.back()')
    self._WaitForNavigation(action_runner)


##############################################################################
# News browsing stories.
##############################################################################


class _NewsBrowsingStory(_BrowsingStory):
  """Abstract base class for news user stories.

  A news story imitates browsing a news website:
  1. Load the main page.
  2. Open and scroll the first news item.
  3. Go back to the main page and scroll it.
  4. Open and scroll the second news item.
  5. Go back to the main page and scroll it.
  6. etc.
  """

  ITEM_READ_TIME_IN_SECONDS = 3
  ITEM_SCROLL_REPEAT = 2
  ITEMS_TO_VISIT = 4
  MAIN_PAGE_SCROLL_REPEAT = 0
  ABSTRACT_STORY = True

  def _DidLoadDocument(self, action_runner):
    for i in xrange(self.ITEMS_TO_VISIT):
      self._NavigateToItem(action_runner, i)
      self._ReadNewsItem(action_runner)
      self._NavigateBack(action_runner)
      self._ScrollMainPage(action_runner)

  def _ReadNewsItem(self, action_runner):
    action_runner.tab.WaitForDocumentReadyStateToBeComplete()
    action_runner.Wait(self.ITEM_READ_TIME_IN_SECONDS/2.0)
    action_runner.RepeatableBrowserDrivenScroll(
        repeat_count=self.ITEM_SCROLL_REPEAT)
    action_runner.Wait(self.ITEM_READ_TIME_IN_SECONDS/2.0)

  def _ScrollMainPage(self, action_runner):
    action_runner.tab.WaitForDocumentReadyStateToBeComplete()
    action_runner.RepeatableBrowserDrivenScroll(
        repeat_count=self.MAIN_PAGE_SCROLL_REPEAT)


# TODO(ulan): Enable this story on mobile once it uses less memory and does not
# crash with OOM.
@decorators.Disabled('android',
                     'win') # crbug.com/665465
class CnnStory(_NewsBrowsingStory):
  """The second top website in http://www.alexa.com/topsites/category/News"""
  NAME = 'browse:news:cnn'
  URL = 'http://edition.cnn.com/'
  ITEM_SELECTOR = '.cd__content > h3 > a'
  ITEMS_TO_VISIT = 2


class FacebookMobileStory(_NewsBrowsingStory):
  NAME = 'browse:social:facebook'
  URL = 'https://www.facebook.com/rihanna'
  ITEM_SELECTOR = 'article ._5msj'
  # We scroll further than usual so that Facebook fetches enough items
  # (crbug.com/631022)
  MAIN_PAGE_SCROLL_REPEAT = 1
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY


class FacebookDesktopStory(_NewsBrowsingStory):
  NAME = 'browse:social:facebook'
  URL = 'https://www.facebook.com/rihanna'
  ITEM_SELECTOR = '._4-eo'
  IS_SINGLE_PAGE_APP = True
  # Web-page-replay does not work for this website:
  # https://github.com/chromium/web-page-replay/issues/79.
  SUPPORTED_PLATFORMS = platforms.NO_PLATFORMS


class FlipboardMobileStory(_NewsBrowsingStory):
  NAME = 'browse:news:flipboard'
  URL = 'https://flipboard.com/explore'
  IS_SINGLE_PAGE_APP = True
  ITEM_SELECTOR = '.grad-top'
  ITEM_SCROLL_REPEAT = 4
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY

  @classmethod
  def ShouldDisable(cls, possible_browser):
    return possible_browser.platform.IsSvelte()  # crbug.com/668097


@decorators.Disabled('mac') # crbug.com/663025
class FlipboardDesktopStory(_NewsBrowsingStory):
  NAME = 'browse:news:flipboard'
  URL = 'https://flipboard.com/explore'
  IS_SINGLE_PAGE_APP = True
  ITEM_SELECTOR = '.cover-image'
  SUPPORTED_PLATFORMS = platforms.DESKTOP_ONLY


# crbug.com/657665 for win and mac, crbug.com/665007 for linux
@decorators.Disabled('win', 'linux', 'yosemite', 'elcapitan')
class HackerNewsStory(_NewsBrowsingStory):
  NAME = 'browse:news:hackernews'
  URL = 'https://news.ycombinator.com'
  ITEM_SELECTOR = '.athing .title > a'


class NytimesMobileStory(_NewsBrowsingStory):
  """The third top website in http://www.alexa.com/topsites/category/News"""
  NAME = 'browse:news:nytimes'
  URL = 'http://mobile.nytimes.com'
  ITEM_SELECTOR = '.sfgAsset-link'
  # Visiting more items causes OOM.
  ITEMS_TO_VISIT = 2
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY


class NytimesDesktopStory(_NewsBrowsingStory):
  """The third top website in http://www.alexa.com/topsites/category/News"""
  NAME = 'browse:news:nytimes'
  URL = 'http://www.nytimes.com'
  ITEM_SELECTOR = '.story-heading > a'
  SUPPORTED_PLATFORMS = platforms.DESKTOP_ONLY


# Desktop qq.com opens a news item in a separate tab, for which the back button
# does not work.
class QqMobileStory(_NewsBrowsingStory):
  NAME = 'browse:news:qq'
  URL = 'http://news.qq.com'
  ITEM_SELECTOR = '.list .full a'
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY


@decorators.Disabled('mac')  # crbug.com/662959
class RedditDesktopStory(_NewsBrowsingStory):
  """The top website in http://www.alexa.com/topsites/category/News"""
  NAME = 'browse:news:reddit'
  URL = 'https://www.reddit.com/r/news/top/?sort=top&t=week'
  ITEM_SELECTOR = '.thing .title > a'
  SUPPORTED_PLATFORMS = platforms.DESKTOP_ONLY


class RedditMobileStory(_NewsBrowsingStory):
  """The top website in http://www.alexa.com/topsites/category/News"""
  NAME = 'browse:news:reddit'
  URL = 'https://www.reddit.com/r/news/top/?sort=top&t=week'
  IS_SINGLE_PAGE_APP = True
  ITEM_SELECTOR = '.PostHeader__post-title-line'
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY


class TwitterMobileStory(_NewsBrowsingStory):
  NAME = 'browse:social:twitter'
  URL = 'https://www.twitter.com/nasa'
  ITEM_SELECTOR = '.Tweet-text'
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY


@decorators.Disabled('win',  # crbug.com/662971
                     'mac')  # crbug.com/664661, crbug.com/663025
class TwitterDesktopStory(_NewsBrowsingStory):
  NAME = 'browse:social:twitter'
  URL = 'https://www.twitter.com/nasa'
  IS_SINGLE_PAGE_APP = True
  ITEM_SELECTOR = '.tweet-text'
  SUPPORTED_PLATFORMS = platforms.DESKTOP_ONLY


class WashingtonPostMobileStory(_NewsBrowsingStory):
  """Progressive website"""
  NAME = 'browse:news:washingtonpost'
  URL = 'https://www.washingtonpost.com/pwa'
  IS_SINGLE_PAGE_APP = True
  ITEM_SELECTOR = '.hed > a'
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY
  _CLOSE_BUTTON_SELECTOR = '.close'

  def _DidLoadDocument(self, action_runner):
    # Close the popup window. On Nexus 9 (and probably other tables) the popup
    # window does not have a "Close" button, instead it has only a "Send link
    # to phone" button. So on tablets we run with the popup window open. The
    # popup is transparent, so this is mostly an aesthetical issue.
    has_button = action_runner.EvaluateJavaScript(
        '!!document.querySelector("%s")' % self._CLOSE_BUTTON_SELECTOR)
    if has_button:
      action_runner.ClickElement(selector=self._CLOSE_BUTTON_SELECTOR)
    super(WashingtonPostMobileStory, self)._DidLoadDocument(action_runner)


##############################################################################
# Media browsing stories.
##############################################################################


class _MediaBrowsingStory(_BrowsingStory):
  """Abstract base class for media user stories

  A media story imitates browsing a website with photo or video content:
  1. Load a page showing a media item
  2. Click on the next link to go to the next media item
  3. etc.
  """

  ABSTRACT_STORY = True
  ITEM_VIEW_TIME_IN_SECONDS = 3
  ITEMS_TO_VISIT = 15
  ITEM_SELECTOR_INDEX = 0
  INCREMENT_INDEX_AFTER_EACH_ITEM = False

  def _DidLoadDocument(self, action_runner):
    index = self.ITEM_SELECTOR_INDEX
    for _ in xrange(self.ITEMS_TO_VISIT):
      self._NavigateToItem(action_runner, index)
      self._ViewMediaItem(action_runner, index)
      if self.INCREMENT_INDEX_AFTER_EACH_ITEM:
        index += 1


  def _ViewMediaItem(self, action_runner, index):
    del index  # Unused.
    action_runner.tab.WaitForDocumentReadyStateToBeComplete()
    action_runner.Wait(self.ITEM_VIEW_TIME_IN_SECONDS)


class ImgurMobileStory(_MediaBrowsingStory):
  NAME = 'browse:media:imgur'
  URL = 'http://imgur.com/gallery/5UlBN'
  ITEM_SELECTOR = '.Navbar-customAction'
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY
  IS_SINGLE_PAGE_APP = True


class ImgurDesktopStory(_MediaBrowsingStory):
  NAME = 'browse:media:imgur'
  URL = 'http://imgur.com/gallery/5UlBN'
  ITEM_SELECTOR = '.navNext'
  SUPPORTED_PLATFORMS = platforms.DESKTOP_ONLY
  IS_SINGLE_PAGE_APP = True


class YouTubeMobileStory(_MediaBrowsingStory):
  NAME = 'browse:media:youtube'
  URL = 'https://m.youtube.com/watch?v=QGfhS1hfTWw&autoplay=false'
  ITEM_SELECTOR = '._mhgb > a'
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY
  IS_SINGLE_PAGE_APP = True
  ITEM_SELECTOR_INDEX = 3


# Failing during CQ runs. crbug.com/661775
@decorators.Disabled('linux', 'win')
class YouTubeDesktopStory(_MediaBrowsingStory):
  NAME = 'browse:media:youtube'
  URL = 'https://www.youtube.com/watch?v=QGfhS1hfTWw&autoplay=false'
  ITEM_SELECTOR = '.yt-uix-simple-thumb-related'
  SUPPORTED_PLATFORMS = platforms.DESKTOP_ONLY
  IS_SINGLE_PAGE_APP = True
  # A longer view time allows videos to load and play.
  ITEM_VIEW_TIME_IN_SECONDS = 5
  ITEMS_TO_VISIT = 8
  ITEM_SELECTOR_INDEX = 3


class FacebookPhotosMobileStory(_MediaBrowsingStory):
  NAME = 'browse:media:facebook_photos'
  URL = (
      'https://m.facebook.com/rihanna/photos/a.207477806675.138795.10092511675/10153911739606676/?type=3&source=54&ref=page_internal')
  ITEM_SELECTOR = '._57-r.touchable'
  SUPPORTED_PLATFORMS = platforms.MOBILE_ONLY
  IS_SINGLE_PAGE_APP = True
  ITEM_SELECTOR_INDEX = 0


class FacebookPhotosDesktopStory(_MediaBrowsingStory):
  NAME = 'browse:media:facebook_photos'
  URL = (
      'https://www.facebook.com/rihanna/photos/a.207477806675.138795.10092511675/10153911739606676/?type=3&theater')
  ITEM_SELECTOR = '.snowliftPager.next'
  # Recording currently does not work. The page gets stuck in the
  # theater viewer.
  SUPPORTED_PLATFORMS = platforms.NO_PLATFORMS
  IS_SINGLE_PAGE_APP = True


class TumblrDesktopStory(_MediaBrowsingStory):
  NAME = 'browse:media:tumblr'
  URL = 'https://tumblr.com/search/gifs'
  ITEM_SELECTOR = '.photo'
  IS_SINGLE_PAGE_APP = True
  ITEMS_TO_VISIT = 8
  INCREMENT_INDEX_AFTER_EACH_ITEM = True
  SUPPORTED_PLATFORMS = platforms.DESKTOP_ONLY

  def _ViewMediaItem(self, action_runner, index):
    super(TumblrDesktopStory, self)._ViewMediaItem(action_runner, index)
    action_runner.MouseClick(selector='#tumblr_lightbox_center_image')
    action_runner.Wait(1)  # To make browsing more realistic.

class PinterestDesktopStory(_MediaBrowsingStory):
  NAME = 'browse:media:pinterest'
  URL = 'https://pinterest.com'
  ITEM_SELECTOR = '.pinImageDim'
  IS_SINGLE_PAGE_APP = True
  ITEMS_TO_VISIT = 8
  INCREMENT_INDEX_AFTER_EACH_ITEM = True
  SUPPORTED_PLATFORMS = platforms.DESKTOP_ONLY

  def _Login(self, action_runner):
    pinterest_login.LoginDesktopAccount(action_runner, 'googletest',
                                        self.credentials_path)

  def _ViewMediaItem(self, action_runner, index):
    super(PinterestDesktopStory, self)._ViewMediaItem(action_runner, index)
    # To imitate real user interaction, we do not want to pin every post.
    # We will only pin every other post.
    if index % 2 == 0:
      # Pin the selection.
      save_function = ('document.querySelector('
                       '".Button.Module.ShowModalButton.btn.hasIcon.hasText.'
                       'isBrioFlat.medium.primary.primaryOnHover.repin.'
                       'pinActionBarButton.isBrioFlat.rounded")')
      action_runner.ClickElement(element_function=save_function)
      action_runner.Wait(1)  # Wait to make navigation realistic.
      # Select which board to pin to.
      inner_save_function = 'document.querySelector(".nameAndIcons")'
      action_runner.WaitForElement(element_function=inner_save_function)
      action_runner.ClickElement(element_function=inner_save_function)
      action_runner.Wait(1)  # Wait to make navigation realistic.

    # Close selection.
    x_element_function = ('document.querySelector('
                          '".Button.borderless.close.visible")')
    action_runner.ClickElement(element_function=x_element_function)
    action_runner.Wait(1)  # Wait to make navigation realistic.
