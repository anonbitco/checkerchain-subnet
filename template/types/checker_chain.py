from typing import List
from typing import Any
from dataclasses import dataclass
import json


@dataclass
class Category:
    _id: str
    name: str

    @staticmethod
    def from_dict(obj: Any) -> 'Category':
        __id = str(obj.get("_id"))
        _name = str(obj.get("name"))
        return Category(__id, _name)


@dataclass
class CreatedBy:
    _id: str
    wallet: str
    username: str
    profileScore: float
    bio: str
    name: str
    profilePicture: str

    @staticmethod
    def from_dict(obj: Any) -> 'CreatedBy':
        __id = str(obj.get("_id"))
        _wallet = str(obj.get("wallet"))
        _username = str(obj.get("username"))
        _profileScore = float(obj.get("profileScore"))
        _bio = str(obj.get("bio"))
        _name = str(obj.get("name"))
        _profilePicture = str(obj.get("profilePicture"))
        return CreatedBy(__id, _wallet, _username, _profileScore, _bio, _name, _profilePicture)


@dataclass
class Day:
    @staticmethod
    def from_dict(obj: Any) -> 'Day':
        return Day()


@dataclass
class Owner:
    @staticmethod
    def from_dict(obj: Any) -> 'Owner':
        return Owner()


@dataclass
class Operation:
    availableAllTime: bool
    _id: str
    days: List[object]

    @staticmethod
    def from_dict(obj: Any) -> 'Operation':
        _availableAllTime = bool(obj.get("availableAllTime"))
        __id = str(obj.get("_id"))
        _days = [Day.from_dict(y) for y in obj.get("days")]
        return Operation(_availableAllTime, __id, _days)


@dataclass
class Reward:
    _id: str
    epoch: int
    product: str
    reviewCycle: int
    __v: int
    createdAt: str
    reward: float
    updatedAt: str

    @staticmethod
    def from_dict(obj: Any) -> 'Reward':
        __id = str(obj.get("_id"))
        _epoch = int(obj.get("epoch"))
        _product = str(obj.get("product"))
        _reviewCycle = int(obj.get("reviewCycle"))
        ___v = int(obj.get("__v"))
        _createdAt = str(obj.get("createdAt"))
        _reward = float(obj.get("reward"))
        _updatedAt = str(obj.get("updatedAt"))
        return Reward(__id, _epoch, _product, _reviewCycle, ___v, _createdAt, _reward, _updatedAt)


@dataclass
class Product:
    _id: str
    name: str
    currentReviewCycle: int
    category: Category
    description: str
    url: str
    location: str
    operation: Operation
    specialReviewRequest: str
    discountCode: str
    offer: str
    subcategories: List[str]
    slug: str
    gallery: List[object]
    teams: List[object]
    twitterProfile: str
    isClaimed: bool
    isClaiming: bool
    network: str
    createdBy: CreatedBy
    owners: List[object]
    status: str
    reviewDeadline: float
    rewards: List[Reward]
    createdAt: str
    updatedAt: str
    __v: int
    logo: str
    coverImage: str
    epoch: int
    consensusScore: float
    normalizedTrustScore: float
    trustScore: float
    lastReviewed: str
    ratingScore: float
    reward: float
    id: str
    reviewCount: int
    subscribersCount: int
    isSubscribed: bool

    @staticmethod
    def from_dict(obj: Any) -> 'Product':
        __id = str(obj.get("_id"))
        _name = str(obj.get("name"))
        _currentReviewCycle = int(obj.get("currentReviewCycle"))
        _category = Category.from_dict(obj.get("category"))
        _description = str(obj.get("description"))
        _url = str(obj.get("url"))
        _location = str(obj.get("location"))
        _operation = Operation.from_dict(obj.get("operation"))
        _specialReviewRequest = str(obj.get("specialReviewRequest"))
        _discountCode = str(obj.get("discountCode"))
        _offer = str(obj.get("offer"))
        _subcategories = [str(y) for y in obj.get("subcategories", [])]
        _slug = str(obj.get("slug"))
        _gallery = [str(y) for y in obj.get("gallery", [])]
        _teams = []
        _twitterProfile = str(obj.get("twitterProfile"))
        _isClaimed = bool(obj.get("isClaimed"))
        _isClaiming = bool(obj.get("isClaiming"))
        _network = str(obj.get("network"))
        _createdBy = CreatedBy.from_dict(obj.get("createdBy"))
        _owners = [Owner.from_dict(y) for y in obj.get("owners")]
        _status = str(obj.get("status"))
        _reviewDeadline = float(obj.get("reviewDeadline"))
        _rewards = [Reward.from_dict(y) for y in obj.get("rewards")]
        _createdAt = str(obj.get("createdAt"))
        _updatedAt = str(obj.get("updatedAt"))
        ___v = int(obj.get("__v"))
        _logo = str(obj.get("logo"))
        _coverImage = str(obj.get("coverImage"))
        _epoch = int(obj.get("epoch"))
        _consensusScore = float(obj.get("consensusScore"))
        _normalizedTrustScore = float(obj.get("normalizedTrustScore"))
        _trustScore = float(obj.get("trustScore"))
        _lastReviewed = str(obj.get("lastReviewed"))
        _ratingScore = float(obj.get("ratingScore"))
        _reward = float(obj.get("reward"))
        _id = str(obj.get("id"))
        _reviewCount = int(obj.get("reviewCount"))
        _subscribersCount = int(obj.get("subscribersCount"))
        _isSubscribed = bool(obj.get("isSubscribed"))
        return Product(__id, _name, _currentReviewCycle, _category, _description, _url, _location, _operation, _specialReviewRequest, _discountCode, _offer, _subcategories, _slug, _gallery, _teams, _twitterProfile, _isClaimed, _isClaiming, _network, _createdBy, _owners, _status, _reviewDeadline, _rewards, _createdAt, _updatedAt, ___v, _logo, _coverImage, _epoch, _consensusScore, _normalizedTrustScore, _trustScore, _lastReviewed, _ratingScore, _reward, _id, _reviewCount, _subscribersCount, _isSubscribed)


@dataclass
class Data:
    products: List[Product]

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        _products = [Product.from_dict(y) for y in obj.get("products")]
        return Data(_products)


@dataclass
class ProductsApiResponse:
    message: str
    data: Data

    @staticmethod
    def from_dict(obj: Any) -> 'ProductsApiResponse':
        _message = str(obj.get("message"))
        _data = Data.from_dict(obj.get("data"))
        return ProductsApiResponse(_message, _data)


@dataclass
class ProductApiResponse:
    message: str
    data: Data

    @staticmethod
    def from_dict(obj: Any) -> 'ProductsApiResponse':
        _message = str(obj.get("message"))
        _data = Product.from_dict(obj.get("data"))
        return ProductsApiResponse(_message, _data)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)
